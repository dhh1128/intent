# Spaces
Intent code and assets is fetched, designed, tested, and transformed into consumable artifacts within a structural container known as a space. Spaces are commonly embodied as a folder hierarchy in a filesystem.

Spaces are similar to concepts such as solution, workspace, or project in many IDEs. However, in intent, the space is itself a first-class language feature that must be fully supported by conforming implementations; although tools are free to decorate or enhance a space with their own metadata, they may not replace it or ignore the semantics associated with its structure.

## motivation

Pragmatism drives this choice. Studies have shown that build frustrations are a major problem for development teams, and that "keeping a build fast and understanding when and how it fails is a key part of improving programmer productivity." This jives with observations from Agile proponents, as well as decades of enterprise software development experience by the designers of intent. Continuous integration servers such as Jenkins, TeamCity, and CruiseControl thrive on normalized, predictable build behaviors--and so does automated testing, as well as sharing and reuse in the FOSS communities.

The lack of a standard for dependency management and project semantics in older languages causes endless headaches as engineers churn on structure in the IDE or build toolset du jour. If you download C++ code that its creator built with scons, but you like to use cmake, you waste hours redefining the build process; if you and your friend don't agree on the relative paths between two components, or if you have installed slightly different library versions, a common formula for building may be expensive or impossible to maintain. Newer approaches (maven, gradle...) have begun to address this problem--but in intent, a robust and satisfying answer is standardized from the get-go.

## filesystem interface

Spaces are not necessarily stored in filesystems; conforming implementations may persist them in a database, front them with WebDAV or a RESTful web service, stream them to and from an object store, compress them in a zip archive, and so forth. However, the interface to a space must be filesystem-like. Each space comprises a coherent namespace, and items within the space are identified contextually by relative path/URL. Items can be thought of as files, and they are manipulated with familiar file operations like copy, move, rename, delete, and edit. Throughout this spec, the terms folder and file should be understood in this light.

All intent code files are encoded with utf-8, without exception. All other text files within a space are also assumed to be encoded with utf-8, unless circumstances demand different treatment (e.g., a non-utf-8 data file is needed as input to a test, specifically to exercise charset handling).

All URLs within a space are segmented with /, regardless of the path separator of the underlying host environment. Because text files are utf-8, whenever URLs appear in files within the space, they are encoded with utf-8, regardless of which charset is active in the underlying host environment. URLs are also percent-encoded (preferably, for reserved characters only, but optionally, with non-reserved characters as well). Conforming implementations are required to recognize percent encodings with only reserved characters, and percent encodings that include additional, unreserved characters, as equivalent. See the wikipedia article for details. For platform independence, URLs within the space should be considered case-sensitive, even when the host environment for the space is more tolerant. None of the behaviors of a space depend on support for symbolic links, although such a feature may offer useful enhancements, and explicitly supporting "shortcut" files similar to .lnk on windows or .desktop on linux is under consideration as a feature.

## grouping concepts

Within a space, items are grouped into folders by component and by aspect. Further grouping may occur by namespace, but that is discussed elsewhere.

A component is a unit of reuse, versioning, and dependency management. Components are fetched and depended upon as a unit; they often include many files and folders. Importantly, components mean something to teams; their boundaries may be a point of handoff between owners, and they may imply differences in location in version control systems. Components may be provided by third parties, sold and licensed, and published to the FOSS community. In colloquial speech, when developers speak about "our custom imaging library" or "the UI" and "the engine," they are probably talking about components. Components may depend on other components at compile time, link time, or (qa) test time. Tools/applications, code from other programming languages, or pre-built binary artifacts may also be components.

An aspect is a view or cross-section within a space, where all constituents of the aspect share a common meaning, orientation, or organizational imperative. For example, all artifacts produced by the build process within a space are part of the space's built aspect (officially named "out"; see below); all of the source code in a space is part of its source aspect (officially named "in"; see below). Note that aspects can span components.

## semantics
As with the *nix Filesystem Hierarchy Standard, certain paths within a space have pre-defined meanings:

|path|meaning|
|----|-------|
|#/in/component|Beneath #/in, components with source code each have exactly 1 component in folder. Although components may have an implicit hierarchy due to their dependency graph, all component folders are siblings, and no nesting is allowed. This allows components to be reused in novel combinations without any changes to assumptions about their relative paths. Each component in folder is allowed to have a different mapping to version control.|
|#/qa|Contains scripts, data, and tests not written or owned by developers. Files in this aspect never serve as input to the build process, and they are only allowed to invoke or inspect files in out folders; they are for "blackbox testing."|
|#/qa/component|Beneath #/qa, components with qa-owned tests each have exactly 1 component qa folder. Each component qa folder is allowed to have a different mapping to version control.|
|doc||
|branding||
|testing||
|output||
|temp||
|l10n||
| |should we just cancel the qa aspect and say that all checked in stuff lives together? That's certainly the way all vcs systems would like to do it, and it facilitates versioning. However, it causes a problem for teams where the qa people check in to a different place from the developers, and the doc people check in to a different place as well, and maybe localizers as well. Maybe we have a logical "qa" aspect that lays down #/in/component/qa and then overlays #/qa/component, so that either is possible?|
|#/|The root of a space. The '#' represents the external environment hosting the space, while the '/' transitions to content "inside" the space. This is analogous to the use of "~/" for a user's home directory in *nix shells.|
|#/space.i|A generated file, not checked in, that contains intent code defining the (semi-)immutable properties of the space, such as which variants, brands, and locales it targets, which components and versions it references, and so forth. These properties are defined by creating an instance of the the space class.|
|#/in|Contains all initial input to the build process -- source code, code for compiled tests owned by developers, scripts to generate installable packages, assets and assets for UIs and documentation, etc. This folder comprises the space's "in" aspect. Typically, files in the "in" aspect are version-controlled. Build activities are not allowed to generate artifacts anywhere below this point in the folder hierarchy.|
|#/out|Contains subfolders that hold all output from the build process -- libraries, binaries, installs, documentation, and so forth. Comprises the space's "out" aspect. Never contains built files directly. This folder does not exist in newly constructed spaces, and is not allowed to contain files that are version-controlled.|
|#/out/std||
|#/out/variant|Subfolders of #/out are known as out folders. Built artifacts that do not vary by platform or build configuration go in #/out/std. Variants may be used to distinguish build types or target platforms: win_with_profiling, ubuntu12_x64, and so forth. In distributed build scenarios, spaces built on multiple machines in parallel, using a shared filesystem, can leverage variant folders to prevent collisions. Deleting out folders is a safe and legal way to fully reset the space to its pristine state. Build activities are allowed to create #/out if it does not exist, and to create an appropriate out folder--but otherwise, they must only generate artifacts within their corresponding out folder.In multi-stage builds, output from an earlier stage of a build, placed in this aspect, may become input to a later stage of the build. Out folders may also be cached, allowing "pre-built" components.|
|#/out/variant/build_outcome.i|A generated file containing intent code that creates an instance of the build outcome class. Describes when the code was last built into this variant, whether the build was successful, what parameters and environmental conditions may have influenced it, and how long it took.|
|#/out/variant/build_log.txt|Contains stdout+stderr from the most recent attempt to build this variant. IDEs can tail or display this file to report build progress.|
|#/out/variant/test_outcome.i|A generated file containing intent code that creates an instance of the test outcome class. Describes when this variant was last tested, whether the test run was successful, what parameters and environmental conditions may have influenced it, and how long it took.|
|#/out/variant/test_log.txt|Contains stdout+stderr from the most recent test run for this variant. IDEs can tail or display this file to report build progress.|
|#/out/variant/component|Within a given out folder, each component that emits artifacts from the build process has exactly one folder.|