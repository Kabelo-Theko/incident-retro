# Motion spec — incident-retro "The Learning Board"

Temperament: **decisive**. One clean write-up per view; zero loops.

## Tokens
```css
--motion:280ms cubic-bezier(.2,0,0,1);
--spring:cubic-bezier(.34,1.26,.5,1);
--emph:cubic-bezier(.05,.7,.1,1);
```

## Choreography (complete)
| Interaction | Animation | Spec |
|---|---|---|
| View render | `.enter` fade + 10px rise | 400ms emph, once |
| Button hover / press | −1px lift / .97 | 130ms spring |
| Library card hover | −2px lift | 130ms spring |
| Field focus | raise to surface + ring | 320ms standard |
| Priority chip update | text/state swap, no animation | instant — data should not dance |
| Theme swap | background transition | 320ms |

No spinners (AI drafting shows a designed text state), no pulses, no loops.

## Reduced motion
Global collapse + `.enter` disabled (v1 guard extended).
