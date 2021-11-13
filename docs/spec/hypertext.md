## Hypertext

Intent is an extremely powerful hypertext format. For clarity and ease of use, it supports most hypertext features from markdown. It also plugs gaps where markdown can't quite match HTML (e.g., the ability to specify a `target` for a link). And it even goes beyond HTML, offering asides, comments, and footnotes/endnotes like a word processor, definition links like ReSpec, and a few hypertext constructs that are totally unique.

### Quick Reference

element | syntax
--- | ---
[normal hyperlink](#hyperlinks) | `[clickable content](ref)`, as in markdown. Advanced params can be added after `ref` using <code>&vert;</code> and `target=x; rel=y` syntax. Unlike HTML or markdown, IML allows nested anchors (e.g., where a full sentence is an anchor, a word inside the sentence can also be an anchor).
[terse hyperlink](#terse-hyperlinks) | `[#clickable content]`, where the clickable content [derives the ID](#comparing-anchor-ids) of an anchor elsewhere. The `#` character is not rendered.
autolinks | Tokens that match URI syntax and that begin with `http://`, `https://`, and `mailto:` are automatically treated as hyperlinks by intent, unless they are immediately preceded by empty braces, as in `[]http://example.com/dont-make-me-clickable`.
[simple text anchor](#simple-text-anchors) | `[anchor text]`. ID is [derived from](#comparing-anchor-ids) anchor text.
[anchor with explicit ID](#explicit-anchor-ids) | `[id: anchor text]`. Only `anchor text` is rendered.
[hidden or empty anchors](#hidden-or-empty-anchors) | `[id:]`
[headers as anchors](#headers-as-anchors) | Same as markdown: `# My header` becomes an anchor referencable as `#my-header`. The space after `#` is required. Unlike markdown, IML allows this to be overridden by inserting an explicit ID at the beginning of the header's content: `# [short-id:]My unwieldy header (and humorous aside)`.
[definition anchor](#definition-text-anchors) | `[=term with definition in surround paragraph]`. Typically referenced with a [terse hyperlink](#terse-hyperlinks).
[code anchors in IPL](#code-anchors) | Automatic from structure; referenced with dotted notation.
[anchors for media and other complex content](#anchor-pairs) | `[id ...]content[/]`. Unlike HTML, overlapping anchors are supported.
[disjoint anchors](#disjoint-anchors) | Add a `+` after at least one instance of a repeated explicit ID: `[id+:anchor text]` and/or `[id+ ...]content[/]`. All content with the same ID becomes part of a single disjoint anchor.

### Anchors

An anchor is a target for a hyperlink -- something we can point *at*. It may be a word or phrase, a location, a visual artifact, or any other type of intent content.

#### Simple text anchors

The most common thing to point at in intent is text, and the simplest way to make it a pointable target is to enclose it in square brackets. For example, the following paragraph defines anchors around two terms, so they can be referenced elsewhere:

```iml
[Magnetic resonance imaging] ([MRI]) is a medical imaging
technique used in radiology to form pictures of the anatomy
and the physiological processes of the body.
```

__Anchor text__ like "Magnetic resonance imaging" in the example above is intended to be visualized inline with the text that surrounds it -- probably un-stylized, and certainly without the square brackets. Enclosing it in square brackets simply delimits the region of the text that can be pointed to:

![simple text anchors](../assets/simple-text-anchors.png)

#### Anchor IDs

Each anchor defines one (or more) __anchor IDs__. This is a short, memorable string that uniquely identifies the anchor within its container.

##### Implicit anchor IDs

The easiest way to define the ID of an anchor is to leave it implicit -- let it be calculated automatically from the anchor text itself. This is what happens with the simple square bracket notation in the MRI example above; the ID for "MRI" is "MRI", too. Or close enough. (See [Comparing anchor IDs below](#comparing-anchor-ids) for more details.)

##### Explicit anchor IDs

It is also possible to customize the ID for an anchor using a more verbose __explicit ID syntax__: `[id: anchor text]`. For example:

```i
The [ww2history: history of World War II] is long and complex.
```

The `id:` prefix can also be added to hyperlinks, making them anchors even as they point elsewhere.

##### ID variants

The same anchor can have multiple ID variants; see [Definition Anchors &gt; Inflection](#inflection) for an example use case and syntax.

##### Comparing anchor IDs

Whether anchor IDs are implicit or explicit, intent recognizes and compares them in a way that makes them convenient and robust for humans. Minor details are ignored: ID values are trimmed, converted to lower case, and have all runs of punctuation and/or spaces replaced with a single hyphen. This means that the anchor id `MRI` could also be written as `mri`. And this contrived example of an ugly ID:

    He won't -- or shouldn't, anyway! -- say "Get lost."

...is the same as:

    he-won-t-or-shouldn-t-anyway-say-get-lost

The lower kabob-case form is canonical. However, variants of this ID that are just capitalized or punctuated differently will also be seen as equivalent.

In addition, *references* to IDs can be abbreviated with an `*` wildcard, as long as the portion of the ID that remains is unambiguous. In most containers, the long ID above could probably be referenced as `He won't*` or `* say 'Get lost'` or even `he*get-lost`.

#### Hidden or empty anchors

Sometimes the intent is to anchor a location, rather than anchoring visible content. For example, you might want to point between two words to show someone where a missing piece of content belongs. To do this, simply insert an explicit anchor ID without any anchor text:

```i
running text[insert-here:] more running text
```

Note the lack of a space after "text". The anchor is for an insert point immediately after "text". If we had instead written:

```i
running text [insert-here:] more running text
```

...the anchor would be between two spaces.

#### Definition anchors and references

In legal and technical documents, it's common to define terms. Often, this is done in the running text of a paragraph. Instances of the term in other places in the doc can then link back to its definition, helping readers who forget the details or consume the content out of order.

Definition anchors in intent facilitate this pattern. They resemble the behavior of `<def>` tags in ReSpec. Where a term is defined, use `[=defined term]` to create an anchor. Where it is referenced, usually [terse link](#terse-links) syntax is optimal: `[#defined term]`.

In the example text about MRIs that we showed above, it might make sense to upgrade to definition anchors, since the paragraph in question actually does provide a definition. The result would look like this:

```iml
[=Magnetic resonance imaging] ([=MRI]) is a medical imaging
technique used in radiology to form pictures of the anatomy
and the physiological processes of the body.
```

Later in the document, we'd reference such a definition this way:

```iml
In certain circumstances, an [#MRI] provides diagnostic insight that is unavailable with a CAT scan. 
```

##### Inflection

But what if we wanted to make our term reference plural: "MRIs provide diagnostic insight..."? Now our clickable term ends with `-s`, whereas its definition is the uninflected singular form... There are two solutions: 

* Add __ID variants__ to the anchor: In the definition anchor, do something like this: `[=MRI[id:MRIs]]`; intent renders only the first form in the *in situ* context, but will accept all others as equally valid variants in references. Variants can include the `*` wildcard; `[=invoking|invoc*|invok*]` creates ID variants that match any form of the verb `invoke`.

    >Note 1: It also creates some nonsense possibilities like accidentally mapping `[#invoc-o-matic]` to the `invoc*` anchor -- but since the author chooses whether to insert such references, and since definition references can only point at definition anchors, there's little practical difficulty with the fuzzy target.

    >Note 2: ID variants are not currently supported for anything except definition anchors. Perhaps they will be supported elsewhere in the future. 

* Just use a traditional hyperlink in the `[clickable text](#id)` form:

    ```iml
    In certain circumstances, [MRIs](#mri) provide diagnostic 
    insight that is unavailable with a CAT scan. 
    ```

#### Code anchors

The structure of [IPL](../glossary#intent-programming-language) source code automatically creates anchors. All formally assigned identifiers (block headers that end in a colon and are followed by indented content) in intent are anchored to their place of definition. In this code:

```i
Register to vote: bool
    params:
        voter
        election
    code:
        # code goes here
```

...the name `Register to vote` is an anchor. So is `Register to vote.params` and `Register to vote.code`.

#### Advanced anchors

Pointing at a simple word or phrase is relatively easy -- but intent supports more sophisticated constructs as well.

##### Anchor pairs

When anchors encompass content that is non-textual, large, or complex, an __anchor pair__ can be used. This is somewhat like a begin tag/end tag pair in HTML. The __anchor start__ contains the anchor ID followed by whitespace and an ellipsis. The __anchor end__ is another bracketed expression that contains the anchor ID preceded by slash:

```i
Sonnet 29 is a famous romantic poem by Shakespeare. 
It goes like this:

    [sonnet-29 ...]
    (all the text of the poem)
    [/sonnet-29]
```

The anchor end only needs enough of the ID from the anchor start to be unambiguous. Often, this could simplify all the way to:

```i
    [sonnet-29 ...]
    (all the text of the poem)
    [/]
```

##### Overlapping anchors

Unlike HTML, anchors in intent do not need to nest cleanly; they can overlap. The following is legal intent code, but requires anchor pairs with at least partial IDs in the anchor ends to make the intent clear:

![overlapping anchors](../assets/overlapping-anchors.png)

##### Disjoint anchors

Intent also supports anchors that encompass multiple, separate stretches of content as a single composite unit. For example, suppose an English teacher wants to illustrate the rhyme scheme in Shakespeare's sonnet. She might define the endings of rhyming lines to be part of a single __disjoint anchor__. When she later links to such an anchor, she is able to point to all items that share a common anchor ID as a unit. In the following example, she could point to the red lines, the blue lines, or the green lines as link targets:

![disjoint anchors](../assets/disjoint-anchors.png)

To define disjoint anchors in intent, use any anchor style(s) with an explicit id, and append a `+` char to at least one instance of the shared anchor ID:

```i
Yet in these thoughts myself almost desp[a+:ising],
Haply I think on thee, and then my [b+ ...]state[/],
Like to the lark at break of day ar[a ...]ising[/]
From sullen earth, sings hymns at heaven’s [b:gate];
For thy sweet love remember’d such wealth [c:brings]
That then I scorn to change my state with [c+:kings].
```

### Hyperlinks

A hyperlink is an expression in the form `[@ref|clickable content]`, where `id` is optional and has the same semantics as with anchors (allowing a hyperlink to also be an anchor itself), `anchor` is a target bracketed elsewhere, and `clickable content` is the text or graphic that would be rendered as blue underlined text if the hyperlink were HTML. Additional params--`target` and `base`--can be added between `anchor` and `linked text` using `;` + whitespace, as in:

```i
[@https://www.example.com/a/b; target=_blank; rel=author|clickable text]
```

Hyperlinks to simple textual anchors can be shortened so they look like those anchors with an `@` in front of them. To refer to the MRI term from our example above, running text might contain the following hyperlink:

```i
You need to get an [@MRI] as soon as possible.
```  

Hyperlinks also support a paired variant that follows the same rules as anchors:

```i
[@https://a.b.com/c; target=_blank ...]clickable content[/] 
```

...or:

```i
[sample@https://a.b.com/c; target=_blank ...]clickcable content[/sample]
```

## Interjections

An interjection lets authors manage linked content where it is convenient to create and maintain -- but display it somewhere else. Interjections are intent's way of dealing with things like footnotes, endnotes, callouts, and similar assets. In an editor, interjections are defined inline: inside, next to, or near the content they enhance. However, they may render in an entirely different place such as a footer or an appendix.

An interjection may have one or more __display points__ where its content or some subset or transformation thereof is rendered. 

A display point for interjection is defined with an expression in the form `[^@id: anchor content]`, where `id` is a formal identifier for the interjection.

The interjected content (e.g., the text of a footnote, the diagram) is defined at a __definition point__. This may be an anchor in the form `[^id: interjected content]`, or a formally named block that has a type, marks, and other properties. In the latter case, the block should carry the `+interject` mark to indicate that it is not to be displayed as part of the running context.

Suppose you are using intent to write about some product requirements, and you want to add a footnote about . You might do it like this:

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




