# Secamoto - brief

Decided: 2026-10-19. Change only on explicit request (redesign, new feature).

## Client
- Business: Hungarian distributor of Seca motorcycle gear (clothing, boots, gloves) plus Richa D3O protectors. Online shop; free pickup in Budapest XVII. by appointment. Company: Moto Central Kft.
- Contact: the shop owner; phone and e-mail in `data/site.json`
- Old site / sources: https://secamoto.hu/ (UNAS webshop, shop id 26165). Facebook and Instagram in `data/site.json`.

## Scope
- Pre-collaboration design demo, not a shop. Every buy button links to the product on secamoto.hu.
- The live shop stays on UNAS until the owner decides. If he says yes, the design moves into UNAS
  (custom design) or a new platform; that is decided then.

## Style
- Base: custom build. Direction: "Dashboard" (Műszerfal): the site framed like a motorcycle TFT screen.
  Riding modes RAIN / ROAD / URBAN / SPORT / TRACK are the main menu. Rev bar and gear indicator in
  the header follow the scroll. Product cards lean into the corner on hover (from the "Paddock"
  direction). The lean-angle badge ("DŐLÉS 44°") was removed on 2026-10-19: it confused visitors. Brainstorm board: https://claude.ai/artifact/3Q7TzKxQhtsVzbfA5ESyXK
- Colours: TFT black #07090B, lit white #E9F1F5, Seca red #FF2335, warning amber #FFB21A, neutral green #2BD47D.
  Fonts: Chakra Petch (dash, headings, numbers) + IBM Plex Sans Condensed (text), self-hosted.
- Keep product and list pages calm: the dash is the frame, not every page.
- Avoid: sci-fi game look, glow everywhere, generated images of people or products.

## Content
- Pages: home (dash + categories), 14 category pages, 5 mode pages, product pages.
- Tone: tegező (motorcycle community), language: Hungarian.
- Prices: gross, as on secamoto.hu. Current campaign (2026-10): clearance, −45% with coupon FINAL45 (`site.json` → `promo`).
- Photos: the shop's own photos, used with the owner's permission. Low-res on the shop: Richa T5 knee
  protector, Drop rain trousers, Dirt Camo T-shirt, Hooligan Air, Clint Camo neck tube. Lifestyle tiles are only 335 px.
- Catalogue: 115 of about 205 products (up to 10 per category), scraped 2026-10-19.

## Bot
- None (user's choice).

## Launch
- Repo: https://github.com/jeszuszkoma/secamoto (public). Demo URL: https://jeszuszkoma.github.io/secamoto/
  (GitHub Pages, `.github/workflows/pages.yml` on every push to main). No Cloudflare Worker.
- noindex until the owner approves.
- Open items: full catalogue sync if the project goes ahead; larger lifestyle photos from the owner or Seca;
  the owner's answer about the clearance sale ("végkiárusítás").
