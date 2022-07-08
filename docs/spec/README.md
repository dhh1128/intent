# Spec

## Introduction

The Intent formal language combines two types of content that have different syntax:

1. [Intent Markup Language (IML)](../glossary.html#intent-markup-language-iml) 
2. [Intent Programming Language (IPL)](../glossary.html#intent-programming-language-ipl)

*Both* types of content have a dual *humans + compilers* audience; IML is more than simple commentary, and IPL is more than machine-readable instructions. 

Note which audience member is listed first. One of the goals of intent is to keep the human audience primary. It does this in many ways -- but one of the most important is that it allows authors to combine powerful exposition and powerful code in a single document. Intent enforces the semantics that connect them.

### IML

IML is a variation of [Github-Flavored Markdown](https://github.github.com/gfm/) (which is in turn a variation of [CommonMark](https://spec.commonmark.org/)). Rather than reproducing a slight variation on the GFM spec here, intent's documentation of IML emphasizes just the differences.

#### Different assumptions

Markdown (a *writing* format) prioritizes the goal of writing content that is readable as plaintext, and transforming it into HTML (a *publishing* format) that can display safely inside a containing website. This means it [favors simple syntax and advocates using inline HTML for advanced constructs](https://daringfireball.net/projects/markdown/syntax#html). But typically, implementations also sanitize various HTML constructs (CSS, `<style>`, `<script>`, many HTML tag attributes, etc.) to prevent [cross-site scripting (XSS)](https://owasp.org/www-community/attacks/xss/#) and [scriptless attacks](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.469.7647&rep=rep1&type=pdf); this means markdown is linmited as a basis for fancy documents.

IML is still a *writing* format, like markdown; it also renders to HTML for publication. However, it prioritizes expressive power and standalone documents more highly. Although most IML is as simple to learn and read as markdown, it has more options for advanced users. And instead of mandating the sanitization of dangerous HTML elements, it defines choices for [transforming](../glossary.html#iml-transformation) in [embeddable mode](../glossary.html#embeddable-mode), [standalone mode](../glossary.html#standalone-mode), or [natural mode](../glossary.html#natural-mode). This preserves safety where it is needed, but allows more nuanced output.

IML also introduces some semantics that extend beyond the limits of ordinary HTML.

#### Transformation modes

For safety and simplicity reasons, intent docs are assumed to intend [embeddable mode](../glossary.html#embeddable-mode) only. The transformation of individual files can always be forced into [standalone mode](../glossary.html#standalone-mode) with the `--standalone-mode` switch. Alternatively, the `--natural-mode` switch will render all files in their [natural mode](../glossary.html#natural-mode).

A file can declare or inherit a `standalone prefix` and/or `standalone suffix` property; the direct declaration of such a prefix or suffix changes the natural mode for the content to standalone. During standalone mode transformation, the content of `standalone prefix` is prepended to the main output as if it were a pure HTML fragment that contained all structure up to and including `<body>`; the content of `standalone suffix` is appended as if it were a pure HTML fragment that contained at least `</body></html>`. 

#### Standalone features

The sanitization of embeddable mode allows the same tags, HTML attributes, and CSS attributes as [HTMLSanitizer's default posture](https://github.com/mganss/HtmlSanitizer#tags-allowed-by-default). Note that this is substantially richer than the set allowed in Github Markdown.

Any HTML constructs beyond this require standalone mode. 

#### Hyperlinks and Anchors

See [hypertext](hypertext.md).

#### Includes

IML supports includes as a convenience.

#### Mustaches

[Mustache templates](https://mustache.github.io/) are supported. A number of predefined metadata variables are defined:

* `{{doc.*}}` &mdash; Document attributes: `size`, `lastmod`, `author`, `commit-hash`, `version`, `relative-path`...
* `{{time.*}}` &mdash; Timestamps in various formats: `yyyy-mm-ddThh:nn:ss.xZ` and similar.
* `{{space.*}}` &mdash; Information about the codebase that contains the doc: `doc-count`, `upstream`, `origin`.

1.1 Hello, World
The “Hello, World” problem domain is too simple to align nicely with intent's positioning, but in the interests of tradition, here is some code for illustration purposes:

hello: app
    Run:
        does:
            Print("Hello, World!")
Intent source files have the file extension .i, and their names and organization within the file system must match certain conventions. Assuming that hello.i is stored in an appropriate directory structure, this code can be compiled using the command line:

intent make hello
...which produces a runnable assembly named hello (*nix/mac) or hello.exe (windows). Its output is:

Hello, World!
The code defines a noun, hello, that is of type app. It then overrides the app's Run verb. It doesn't bother declaring the parameters, return type, visibility, or scope binding for this verb, since they are all defined in the app base class; it simply provides implementation of the logic in the does block.

Unlike many programming languages, there is no main() in intent. Instead, we use a verb named Run on a class that inherits app as a starting point for execution, but there is more going on under the hood than simple convention. This will be discussed in greater detail later.


1.2 core concepts
You may have noticed that the preceding discussion used terms like noun and verb. If you were wondering why you didn't see terms like class and method, instead, then have no fear; they'll show up. But intent builds these ideas off more primitive constructs, modeled on human language:

name
Names in intent are phrases. They can include spaces. Many problems with traditional programming ecosystems are traceable to ambiguity, clumsiness, or verbosity of names. Intent provides elegant solutions, including aliasing and smart abbreviation; more on this later.
noun
A name-able, instantiate-able concept. The foundational building block of intent semantics. In intent, nouns are usually named by descriptive noun phrases in lower case, such as file system, phase of the moon, or user.
verb
A particular category of concept (and thus, a specialized sort of noun) that conveys an action or state of being. In intent, all verbs are named by descriptive verb phrases that begin with an upper-case letter, such as Prepare for lift-off, Is busy, or Sleep.
mark
A descriptive semantic payload that is bound to a noun or verb. Marks play the same role in intent as adjectives and adverbs play in many human languages; however, they have special characteristics that aid semantic formalism, so they go by their own name. Some of their behaviors are inspired by the phenomenon of markedness in linguistics. To convey the idea that a str parameter cannot be empty, we might bind a -empty mark to it. Marks are one of the most unique and powerful concepts in intent.
definition
The process of naming a noun, describing its meaning and semantics, and possibly associating it with a value. This declarative pattern is very frequent in intent. For example, percentile: +range[0,100) = 10 is a variable declaration that embodies the definition pattern; it defines an integer variable with a valid range from 0 to 99, inclusive, and it assigns the initial value of 10 to it. In the hello world sample above, only the final line is not a definition.

1.3 building blocks
The low-level structure beneath statements is formally specified later. In this overview, let's focus instead on how progressively higher-order constructs are built.

statement
The smallest unit of intent code that can be analyzed or executed on its own; this meaning matches that of the term in most other programming languages. Continuing our analogy to human language, a statement is like a sentence. An example of a statement might be: my size = 3. In most cases, statements are not terminated with any punctuation--just a line break.
block
A sequence of statements that share a common bounding context or scope. Again, this matches the meaning you'd expect from other programming languages. Intent uses indents to delimit blocks, in much the same style as python. However, it requires that all indenting be done with the same strategy--either uniform spaces, or uniform tabs.
compilation unit
A sequence of statements and/or blocks that should be edited/parsed/compiled together. Generally, intent code is persisted to files, and each file is a separate compilation unit. Rules govern what may be unified in a compilation unit. Implementation of a given class or other noun may be spread across multiple compilation units (a feature called partial classes in C#). The mime type for an intent compilation unit is "text/x-intent-compilation-unit".
persistence strategy
A method for storing and retrieving a representation of intent code. The default persistence strategy for intent is "file system persistence", which stipulates that compilation units end in the .i file extension, and that the folder hierarchy be organized in a particular way. Other persistence strategies include "RESTful persistence" and "RDBMS persistence", which allow intent to be backed by different mechanisms for direct, online, collaborative editing.
module
A grouping of intent functionality that facilitates encapsulation and internal dependency management. Modules provide formal interfaces, consumable by other programmers with a Use(...) statement. All content of a module shares a unifying namespace (though a namespace may contain more than one module). Module interfaces are versioned and can be tested for compatibility. They also have rich metadata, including a maturity (which describes the module's evolution through a release lifecycle), a license, and so forth. Members of the same module can potentially see data that is invisible beyond the firewall of the module's interface.

A class in intent may be exposed as a module. A single class cannot span module boundaries, and a module usually contains only a single major class. However, module is not a synonym for class. A collection of string-handling routines might be modeled as a module even though they are not bound to a class--and some classes might never be exposed in a module interface.

Modules are the unit of linkage in intent. If all compilation units pertaining to a module build successfully, then the module can be linked. Within a component, dependencies are expressed on a module basis.

In intent's file system persistence strategy, a module always corresponds to a single folder. The modules in software that control the targeting system on USS Enterprise's bridge might include:

range finder
motion tracker
power pack
weapon selector
package
A way to group related items for namespacing and convenient distribution. Generally, packages are used to unify a problem domain, such as "traffic routing" in a GPS system, or "protein folding" in genomics. Unlike modules, packages do not have formal interfaces, are not versioned, and may have unbounded membership (more than one codebase may declare members of the same package).

In intent's file system persistence strategy, a package always corresponds to a folder. Like java, intent prescribes a general-to-specific hierarchy in package names. However, unlike java, intent package folders are not nested, so all packages are direct siblings of one another--and convention in intent does not dictate that package names begin with a top-level internet domain name. The package structure for software on the USS Enterprise's bridge might include:

crew.people
crew.quarters
crew.roles
federation.charts
federation.races and civilizations
mission
ship.power
ship.propulsion
ship.sensors
ship.shields
component
The unit of intent code reuse and recomposition that (at least theoretically) has its own build, integration status, repository, team members, backlog, and project schedule. If you're building an enterprise product and a consumer product that both share the same underlying engine, then the engine is probably its own component, and the unique enterprise-ish or consumer-ish veneers that sit atop the engine are separate components as well.
assembly
Compiled output from a component, packaged as a single binary file. These may be runnable assemblies, in which case they have the executable bit set on *nix, or the .exe extension on windows. Runnable assemblies may have dependencies; the fact that they are runnable does not guarantee self-sufficiency. The term program is colloquially used as a synonym, but is deprecated by intent because of its ambiguity.

Alternatively, assemblies may lack an entry point, but contain collections of reference behavior; such collection assemblies have the .icoll file extension.

Either type of intent assembly supports code signing, versioning, and other rich meta data via a manifest.

A third possibility is a foreign assembly. These are *.so/*.dll or *.a/*.lib files. Intent does not produce such artifacts, but it can consume them. See collection assemblies for a discussion of how intent provides the functionality in traditional libraries.

zoan
Zoan (2 syllables; plural form is zoa) comes from the Greek word for animal--and as the name implies, these entities have a life cycle. They are spawned and eventually die. They may evolve and reproduce. They act. The analog with biology is reflected in the terms for other high-level building blocks in intent; it provides a conceptual framework for many formal concepts that are missing in other approaches.

The genome for a zoan is stored in the set of one or more assemblies that, as a unit, can reproduce a zoan's top-level process group on a machine. For example, an intent runnable assembly named ‘helloworld’ might depend on a collection assembly for fancy screen painting, plus the C++ runtime (foreign assembly). The combination of these three assemblies is loaded by a machine when helloworld runs; thus, the trio constitutes a zoan.

In non-intentional contexts, this concept sometimes goes by the name application or app, and in casual speech, that terminology may be close enough. However, the general usage of these terms is broader than the meaning of zoan in intent (some "applications" are actually composed of multiple zoa); compare the discussion of co-op below.

The runnable assembly that forms the nucleus of a zoan provides a unique species id which is usually stable over time. Conceptually, this identifier may be distinct from the unique identifier of the runnable assembly itself (as might be the case where a single runnable assembly provides different feature sets depending on how it's named or configured, or where it's installed).

machine
A computer (in the CS sense) that runs zoans. Machines may be physical hardware or virtual machines. They may be in-between constructs that blur these lines (such as linux virtual containers). They may be Java Virtual Machines or similar sandboxed environments. What they have in common is that they provide resources and services inside of which zoans run.

Individual zoans never cross machine boundaries.

community
A group of zoans, typically of different species, that interacts with a designed purpose. In the case of a classic web app, intent would describe the server-side back end, the DBMS, the web server, and the client-side UI in the browser as separate zoans, and the combination as a community.

All interactions within an intent community are remotable, such that the community can live on a single machine, or be distributed across many, with minimal fuss.

Communities may be combined or nested to build increasingly complex structures, performing increasingly sophisticated work. Depending on its granularity, an intent community might map onto the industry terms application/app, product, or suite.

habitat
An environment that hosts software. This may be as simple as a single machine, but more typically it involves multiple machines, the infrastructure that connects them, the framework that manages them, and the services that the framework provides:

EC2, GCE, and Azure are examples of public cloud habitats.
OpenStack can be used to build a private cloud habitat.
BOINC-like distributed compute farms are habitats.
A supercompute cluster–or a grid of such clusters is a habitat.
Hybrid, federated, and custom fabrics are also possible.
population
The set of all processes within a habitat that are of the same zoan species.
ecosystem
One or more habitat instances, and the communities of zoans and co-ops that interacts within it.
biote
A "living" system at any level of detail--a zoan, a community, a population, or an ecosystem.
user
An independent entity, external to a biote, that interacts with it. People and other systems of software are two important types of user. Users often make demands on biotes, and they may also have responsibilities with regard to it.
flow
The interface that describes interaction patterns embodied in a biote. A flow is a first-class construct in intent; it is possible to test a community for conformance to a flow in which it participates.