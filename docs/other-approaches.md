# Other approaches

Most modern programming languages are imperative. As a rough approximation, we can say that they focus on telling a computer what to do. When you read code in Assembly, Java, C#, C++, D, Python, Ruby, PHP, VB, ActionScript, JavaScript, Ada, Eiffel, shell scripts, or even Excel macros, you mostly see sequences of instructions that the program follows as it executes. Object-oriented programming encapsulates state and provides convenient abstractions, but it largely adopts this paradigm.

A few programming languages are functional. They avoid state and mutable data as much as possible, and focus on describing how to compute. Lisp, Scheme, Clojure, Erlang, OCaml, Haskell, Scala, F#, and xslt fit into this category.

Plenty of hybrid or exotic approaches exist, but history shows that they struggle with obscurity.

It is possible to write great code in any of these languages, if conditions are right and commitment is high. However, they all share a pervasive weakness: these languages treat the computer as the only audience that matters, and relegate people to afterthought status. In other words, [they ignore why](why.md).

Within the bounds of a context-free grammar, programmers can use lousy names, horrible organization, inconsistent design, and utterly opaque meaning--and no compiler will complain. They can fail to address a requirement, forget about a category of user, do nothing to handle errors responsibly, and write no tests--and no compiler will complain. They can confuse the heck out of their teammates--and no compiler will complain.

We need something better.

We need a paradigm that elevates people to a primary concern, and that answers the overriding question that makes our thinking so very un-machine-like: *Why*? What is the intent?