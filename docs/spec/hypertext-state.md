State machine for parsing hypertext

&nbsp; | [ | [+ | [= | [# | : | \] | @ | other | EOL
 --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
(null) | push in-hyper | push need-id | push in-def | push in-terse | no change | no change | no change | no change | no change
in-hyper (hypertext of unknown type) | push in-hyper | push need-id | push in-def | push in-terse | no change | goto in-empty (might have ID) | goto in-link | goto in-anchor | E1: expected ] x recursed layers
need-id | E2: can't put hypertext here | E2 | E2 | E2 | E3: expected ID | E3 | E3 | goto need-colon | E3 + E1
need-colon | E2 | E2 | E2 | E2 | goto in-hyper | E4: expected colon | E4 | no change | E4 + E3 + E1
in-anchor | push in-hyper | push need-id | push in-def | push in-terse | no change | save ID; pop | no change | no change | E1
in-def | push in-hyper | push need-id | push in-def | push in-terse | no change | save ID; pop | no change | no change | E1
in-terse | push in-hyper | push need-id | push in-def | push in-terse | no change | save ref; pop | no change | no change | E1
in-empty | E5: useless empty; pop; push in-hyper | E5; pop; push need-id | E5; pop; push in-def | E5; pop; push in-terse | E5; pop | E5; pop | E5; pop | if ( goto show-raw else E5; pop | E5
in-link | need special handling of ; and x=y for params

