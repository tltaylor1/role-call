# role-call

role-call inventories the non-human identities in a cloud account: the
roles, service accounts, and access keys that get created, granted
permissions once, and forgotten. It gives each identity an owner, the
context nobody has (when it was last used, what it can do versus what it
actually does, how old its credentials are), and a recertification path, so
machine identities get governed the way human access already is.

It starts with Amazon Web Services (AWS) identity.

**Status: Phase 0, design.** No application code exists yet. The
architecture, threat model, and roadmap arrive with the first commits, and
the code follows the design rather than preceding it.
