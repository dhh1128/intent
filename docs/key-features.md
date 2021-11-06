## Key Features

Intent is a programming language with a hybrid paradigm that incorporates the best of imperative, functional, and declarative approaches. It is object-oriented, type-safe, concurrency-savvy, and [general-purpose (but systems- rather than UI-focused)](positioning.md). It can call C libraries (.so, .dll, .dylib) as well as java and other JVM-based languages. Intent compiles down to native binaries for C-like performance, or it can be translated to JVM byte code, python, C++ 11, or other high-level syntaxes.

### Unique

feature | comment
--- | ---
marks | Lets programmers declare semantics and intent in a human-friendly way, with compiler enforcement. [more]
code as hypertext | Any statement, file, folder, or other structure unit can be the anchor of a hyperlink. Code can formally link to other sites, and can have attachments. [more]
collaborative compilation | Compiler carries out housekeeping tasks based on programmer hints. Warnings are questions that programmers can eliminate by answering. Answers are sticky. [more]
polyglot compilation | Compiles to various targets including other high-level languages. [more]
generated interfaces | For each public class, the analog to a C++ header is generated from the implementation, by the compiler. This lets producers of a class write implementation only, without worrying about maintaining a second file &mdash; while at the same time allowing consumers to code against a pure interface. Interfaces are automatically versioned in an intelligent way. [more]
statements instead of lines | Uses a unique approach to line wrapping that eliminates a lot of tedious reformatting. [more]
names with spaces | Identifiers in intent can (and usually do) have spaces. [more]
step routines and stubs | Complex routines can be split into bite-sized chunks easily. Stubs can be declared with minimal fuss, and the compiler will implement them. [more]
integrated roles, stories, scenarios, and epics | Many agile best practices are reflectable (or required) in code constructs. [more]
constructs higher than application | Supports fabric-wide configuration, discovery, and message exchange. [more]
lifecycles | Requires object state evolution to be formally modeled, which drastically simplifies troubleshooting and maintenance. [more]
problems and circuit-breakers | Allows declaration of conditions that should trigger escalations elsewhere in a codebase. These declarations can be injected in IoC pattern. [more]
optional garbage collection | By default, uses deterministic destructors and an RAII style of resource management. However, can be translated to a GC world for interop with java and similar environments. [more]
semantic interface compatibility | Can test for compatible interface overlap instead of exact interface versions. [more]

### Familiar but cool

feature | comment
--- | ---
design by contract | Makes declaring and enforcing preconditions and postconditions easy.
closures and lambdas | Pass execution state to other parts of a program.
actor model | Approaches concurrency like Erlang or Scala, with a few tweaks. Includes Erlang's notion of supervisors of processes. [more]
nested constructors | Call one constructor from another to avoid writing boilerplate code. Compare to C++ 11.
meta code | Write code that performs static assertions, code generation, and much more. Think macros, cleanly implemented, on steroids.
generics | Containers, classes, and algorithms that are templatized by type. Variadic generics.
very robust string and regex handling | Not as rich as perl, but close.
universal function call syntax | Call a function with first arg = class instance, just like it was a member of the class. Allows classes to be extended after compilation. Compare to D.
scope exit handlers | Define what will happen if you leave a scope with failure, early success, or normal success.
AOP and dependency injection | Define aspects; inject behaviors in a way that cross-cuts codebases.
and of course... | xUnit-based testing (spock-compatible), reflection, unicode and localization support, REPL, docs from code comments, and lots of other standard goodies.