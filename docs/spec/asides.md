# Asides

An __aside__ is a piece of content that is related to but separate from the main flow of a document. In an editor, asides are defined inline: inside, next to, or near the content they enhance. However, they may render in an entirely different place such as a footer or an appendix. Intent uses asides for things like footnotes, endnotes, and callouts. 

An aside has one or more __display points__ where its content or some subset or transformation thereof is rendered.

A display point for an aside is defined with an expression in the form `[^@id: anchor content]`, where `id` is a formal identifier for the interjection.

The aside content (e.g., the text of a footnote, the diagram) is defined at a __definition point__. This may be an anchor in the form `[^id: aside content]`, or a formally named block that has a type, marks, and other properties. In the latter case, the block should carry the `+aside` mark to indicate that it is not to be displayed as part of the running context.

Suppose you are using intent to write about some product requirements, and you want to add a footnote about accessibility. You might do it like this:

```i
We need to make sure that we consider accessibility. Some of our
customers [^@1: say] that they won't buy unless the product is
usable by the visually impaired.

[^1: See the focus group done in Sep 2019.]
```

You could also do it like this:

```i
We need to make sure that we consider accessibility. Some of our
customers [^@1: say] that they won't buy unless the product is
usable by the visually impaired.

^1: footnote
    See the focus group done in Sep 2019.
```



