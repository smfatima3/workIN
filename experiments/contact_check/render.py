"""Render all 24 scripted calibration trajectories from recorded MuJoCo positions."""
import argparse
import json
from pathlib import Path
import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BG = '#f2f5f7'
INK = '#142e42'

def font(size):
    for name in ('C:/Windows/Fonts/arial.ttf', 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)

def render(root):
    root = Path(root)
    dest = root / 'videos'
    dest.mkdir(exist_ok=True)
    titles = {'A_standard': 'A — Supported placement and edge release',
              'B_standard': 'B — Curved route and direct route',
              'C_standard': 'C — Release during moving transfer',
              'C_paused': 'C — Release during paused transfer'}
    manifest = []
    for case, title in titles.items():
        trials = [[json.loads((root / 'trials' / f'{case}_{arm}_{offset:+.2f}' / 'evidence.json').read_text())
                   for arm in ('reference', 'challenge')] for offset in (-.02, 0., .02)]
        output = dest / (case + '.mp4')
        with imageio.get_writer(output, fps=12, codec='libx264', quality=8, macro_block_size=16) as writer:
            for frame in range(96):
                im = Image.new('RGB', (1280, 960), BG)
                d = ImageDraw.Draw(im)
                d.text((22, 12), title, font=font(26), fill=INK)
                d.text((22, 49), 'Scripted MuJoCo calibration · measured positions · fixed person proxy', font=font(18), fill=INK)
                d.text((22, 77), 'Reference action', font=font(22), fill=INK)
                d.text((662, 77), 'Challenge action', font=font(22), fill=INK)
                for row, pair in enumerate(trials):
                    for col, trial in enumerate(pair):
                        left, top = 16 + col * 640, 112 + row * 276
                        data = trial['frames'][round(frame * (len(trial['frames']) - 1) / 95)]
                        x, y, z = data['position_m']
                        px, py, pz = trial['person_position_m']
                        hit = data['contact_so_far']
                        def point(a, b):
                            return left + 290 + a * 270, top + 207 - b * 150
                        d.rounded_rectangle((left, top, left + 624, top + 266), radius=8, fill='white', outline='#cad5dc')
                        d.text((left + 12, top + 8), f"Person x offset {trial['offset_m']:+.2f} m · t {data['time_s']:.3f} s", font=font(17), fill=INK)
                        if case.startswith('B'):
                            def point(a, b):
                                return left + 300 + a * 320, top + 183 - b * 240
                            d.text((left + 12, top + 32), 'Top view', font=font(15), fill='#526575')
                            goalx, goaly = point(.70, 0)
                            d.ellipse((goalx-9, goaly-9, goalx+9, goaly+9), outline='#337555', width=3)
                            person = point(px, py)
                            d.ellipse((person[0]-32, person[1]-24, person[0]+32, person[1]+24), fill='#cf5c4d' if hit else '#5c9295')
                            path = [point(*f['position_m'][:2]) for f in trial['frames'][:round(frame*(len(trial['frames'])-1)/95)+1]]
                            if len(path)>1:
                                d.line(path, fill='#c6915a', width=3)
                            center = point(x,y)
                            d.rectangle((center[0]-.095*320,center[1]-.075*240,center[0]+.095*320,center[1]+.075*240), fill='#a6622c')
                        else:
                            d.text((left + 12, top + 32), 'Side view', font=font(15), fill='#526575')
                            d.line((*point(-.95,0),*point(.95,0)),fill='#aebbc2',width=2)
                            if case.startswith('A'):
                                d.rectangle((*point(-.82,.84),*point(.14,.76)),fill='#9daeb6')
                            d.rounded_rectangle((*point(px-.1,pz+.25),*point(px+.1,pz-.25)), radius=15, fill='#cf5c4d' if hit else '#5c9295')
                            d.rectangle((*point(x-.095,z+.065),*point(x+.095,z-.065)),fill='#a6622c')
                        events = trial['contact_steps']
                        status = f"Contact moving ↔ person · first t {events[0]['time_s']:.3f} s" if hit else 'No scored contact yet'
                        d.text((left+12, top+232),status,font=font(17),fill='#a72c24' if hit else INK)
                d.text((22, 946-12), '8-second replay of 1.90 simulated seconds · contact label persists after first contact',font=font(16),fill=INK)
                writer.append_data(np.asarray(im))
                if frame == 78:
                    im.save(dest/(case+'.png'))
        manifest.append({'scenario':case,'file':output.name,'duration_s':8,'fps':12,'frames':96,
            'offsets_m':[-.02,0,.02],'arms':['reference','challenge'],'selection':'all 24 supplied trial specifications',
            'view':'top' if case.startswith('B') else 'side','contact':'MuJoCo moving/person positive normal force'})
    (dest/'manifest.json').write_text(json.dumps(manifest,indent=2))

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',required=True)
    render(parser.parse_args().root)
