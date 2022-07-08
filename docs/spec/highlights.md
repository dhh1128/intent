# Highlights

Highlights are intent's way of adding visual overlays to text,[^1] much as markers or colored pencils can mark up paper documents. Highlights may be used for scholarly analysis, feedback, or meta commentary.

Highlights can be added to an intent document by original authors and by subsequent readers. Highlights are organized into layers, and individual layers can be shown or hidden.

Highlights are visualized with subtle color and lines, and exhibit helpful behaviors on mouse-over and click events. This allows semantic richness without overwhelming the text itself. However, it introduces a challenge: in modern browsers and editors, color and layout are influenced by many external factors such as light/dark theme, accessibility settings, and screen resolution. Therefore, the creator of a highlight gives only hints about its appearance (e.g., a base color and style); exact rendering is reserved for code that tweaks alpha channel and other characteristics to suit the circumstances. 

{
[1]: Conceptually, intent highlights resemble a `<span>` in HTML; the goal is to paint a region of text with additional semantics. However, the correspondence is not perfect. As their name implies, intent highlights are always intended to create a visual effect; HTML `<span>` tags may have a non-visual purpose.
}

effect | rendering | syntax
--- | --- | ---
marker highlight | Apply a background color to text; intensify the color on hover. | `[~ marked text]` for default orange (`#ffa500`). Colors can also be named: `[~red~ marked text]` or specified by 3-char RGB triple: `[~808~ marked text]` (for purple). Note that colors are used as the basis of the visual effect, but are not rendered exactly as given; their alpha channel is adjusted.
box highlight | A lightly visible (mostly transparent) bounding rectangle is drawn. Color of the rectangle, and all other rectangles with the same appearance, intensifies on hover. | <code>[&vert; boxed text]</code> for gray. Colors can also be named or specified by 3-char RGB triple: <code>[&vert;blue&vert; text]</code> or <code>[&vert;e93&vert; text]</code> (for orange)
underline highlight | A lightly visible (mostly transparent) underline is drawn; this is different from a simple html `<u>` in that the underline does not have the same color as the text. Color of the underline, and all other underlines with the same appearance, intensifies on hover. | `[_ underlined text]` for gray.
placeholder highlight | A dotted box, lightly shaded, is created to show that something is missing.
