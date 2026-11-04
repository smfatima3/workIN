# These are transparent benchmark controls, NOT reproductions of named papers.
CONDITIONS={
 'A':dict(poison=False,persistent=True,defense='none'),
 'B':dict(poison=True,persistent=True,defense='none'),
 'C':dict(poison=False,persistent=False,defense='none'),
 'D':dict(poison=True,persistent=False,defense='none'),
 'E':dict(poison=False,persistent=True,defense='verify_on_use'),
 'F':dict(poison=True,persistent=True,defense='verify_on_use'),
}
for name in ['ttl','full_reset','lineage_revoke','source_only','local_shield','verify_at_write']:
    for poison in [False,True]:
        CONDITIONS[name+('_poison' if poison else '_clean')]=dict(poison=poison,persistent=True,defense=name)
CONDITIONS['stale']=dict(poison=False,persistent=True,defense='none',stale=True)
CONDITIONS['isolated_clean']=dict(poison=False,persistent=True,defense='none',isolated=True)
CONDITIONS['isolated_poison']=dict(poison=True,persistent=True,defense='none',isolated=True)
