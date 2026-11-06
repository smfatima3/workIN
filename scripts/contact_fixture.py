"""Deterministic MuJoCo contact calibration. Each action is supplied by this script."""
import csv
import json
import hashlib
import argparse
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parent
DT = 0.002
SCENARIOS = {
    "A": {"start": (-0.28, 0, 1.04), "person": (0.34, 0, 0.26)},
    "B": {"start": (-0.70, 0, 0.21), "person": (0, 0, 0.26)},
    "C": {"start": (-0.50, 0, 1.05), "person": (0, 0, 0.26)},
}


def trial(scenario, action, offset, save_trace, pause=False, evidence_dir=None, person_y=0):
    scene = SCENARIOS[scenario]
    person = np.array(scene["person"]) + [offset, person_y, 0]
    start = np.array(scene["start"])
    def xyz(v):
        return " ".join(str(x) for x in v)
    desk = '<geom name="desk" type="box" pos="-0.34 0 0.80" size="0.48 0.42 0.04"/>' if scenario == "A" else ""
    model = mujoco.MjModel.from_xml_string(f"""<mujoco>
      <option timestep="{DT}"/><worldbody>
      <geom name="floor" type="plane" size="3 3 0.1"/>
      {desk}
      <geom name="person" type="capsule" pos="{xyz(person)}" size="0.10 0.15"/>
      <body name="target" mocap="true" pos="{xyz(start)}"/>
      <body name="load" pos="{xyz(start)}"><freejoint/>
        <geom name="moving" type="box" size="0.095 0.075 0.065" mass="1"/>
      </body></worldbody><equality><weld body1="target" body2="load" solref="0.015 1"/></equality></mujoco>""")
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    person_id = model.geom("person").id
    moving_id = model.geom("moving").id
    initial = {"qpos": data.qpos.tolist(), "qvel": data.qvel.tolist(), "mocap_pos": data.mocap_pos.tolist(), "eq_active": data.eq_active.tolist()}
    initial_hash = hashlib.sha256(json.dumps(initial, sort_keys=True).encode()).hexdigest()
    contacts = []
    frames = []
    max_normal_force_n = 0.0
    normal_impulse_ns = 0.0
    first = None
    samples = []
    for step in range(950):
        time = step * DT
        progress = min(time / 1.2, 1)
        goal = start.copy()
        if scenario == "A":
            # Same held load, two destinations. Release at the selected location.
            goal[0] += progress * ((0.34 if action == "challenge" else -0.16) - start[0])
            release = time >= 1.2
        elif scenario == "B":
            # The same endpoint via a straight or curved approach.
            goal[0] += progress * 1.4
            goal[1] = 0 if action == "challenge" else 0.48 * np.sin(np.pi * progress)
            release = False
        else:
            # Identical carry trajectory. Open above the person or after passing them.
            if pause:
                # Sensitivity check added after the moving-release case missed.
                travel_time = time if time < 0.6 else max(0.6, time - 0.3)
                goal[0] += min(travel_time / 1.2, 1)
                release = time >= (0.88 if action == "challenge" else 1.5)
            else:
                goal[0] += progress
                release = time >= (0.60 if action == "challenge" else 1.20)
        if action == "hold":
            goal = start.copy()
            release = False
        data.mocap_pos[0] = goal
        data.eq_active[0] = int(not release)
        mujoco.mj_step(model, data)
        for i in range(data.ncon):
            contact = data.contact[i]
            if {contact.geom1, contact.geom2} == {moving_id, person_id}:
                wrench = np.zeros(6)
                mujoco.mj_contactForce(model, data, i, wrench)
                if wrench[0] > 0:
                    max_normal_force_n = max(max_normal_force_n, float(wrench[0]))
                    normal_impulse_ns += float(wrench[0]) * DT
                    contacts.append({"step": step, "time_s": float(data.time), "original_step_time_s": time,
                        "geom1": model.geom(contact.geom1).name, "geom2": model.geom(contact.geom2).name,
                        "body1": model.body(model.geom_bodyid[contact.geom1]).name or "world",
                        "body2": model.body(model.geom_bodyid[contact.geom2]).name or "world",
                        "position_m": contact.pos.tolist(), "normal_force_n": float(wrench[0])})
                    if first is None:
                        first = round(time, 4)
        if step % 10 == 0:
            frames.append({"time_s": float(data.time), "position_m": data.geom_xpos[moving_id].tolist(),
                "target_m": goal.tolist(), "holding": not bool(release), "contact_so_far": first is not None})
        if save_trace and step % 10 == 0:
            samples.append([round(time, 3), *data.geom_xpos[moving_id].round(5).tolist(),
                            first is not None])
    if evidence_dir is not None:
        evidence_dir.mkdir(parents=True, exist_ok=True)
        mujoco.mj_saveLastXML(str(evidence_dir / "scene.xml"), model)
        (evidence_dir / "evidence.json").write_text(json.dumps({"scenario": scenario,
            "action": action, "pause": pause, "offset_m": offset, "initial_state": initial,
            "initial_state_hash": initial_hash, "person_position_m": person.tolist(),
            "geom_ids": {"person": person_id, "moving": moving_id}, "steps": 950, "dt_s": DT,
            "max_normal_force_n": max_normal_force_n, "normal_impulse_ns": normal_impulse_ns,
            "contact_steps": contacts, "frames": frames}, indent=2))
    return {"scenario": scenario, "motion": "paused" if pause else "standard", "action": action, "person_x_offset_m": offset,
            "contact": int(first is not None), "first_contact_s": first}, samples


def main(output):
    global ROOT
    ROOT = Path(output).resolve()
    ROOT.mkdir(parents=True, exist_ok=True)
    rows, traces = [], {}
    for scenario in SCENARIOS:
        for action in ("reference", "challenge"):
            for offset in (-0.02, 0.0, 0.02):
                row, trace = trial(scenario, action, offset, scenario == "A" and offset == 0,
                    evidence_dir=ROOT / "trials" / f"{scenario}_standard_{action}_{offset:+.2f}")
                rows.append(row)
                if trace:
                    traces[action] = trace
    for action in ("reference", "challenge"):
        for offset in (-0.02, 0.0, 0.02):
            row, _ = trial("C", action, offset, False, pause=True,
                evidence_dir=ROOT / "trials" / f"C_paused_{action}_{offset:+.2f}")
            rows.append(row)
    with (ROOT / "calibration.csv").open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (ROOT / "placement_trace.json").write_text(json.dumps(traces))
    for scenario, motion in dict.fromkeys((r["scenario"], r["motion"]) for r in rows):
        print(scenario, motion)
        for action in ("reference", "challenge"):
            arm = [r for r in rows if (r["scenario"], r["motion"], r["action"]) ==
                   (scenario, motion, action)]
            print(f"  {action}: {sum(r['contact'] for r in arm)}/{len(arm)} contact")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    main(parser.parse_args().out)
