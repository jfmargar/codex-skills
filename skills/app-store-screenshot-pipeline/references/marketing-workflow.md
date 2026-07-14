# Marketing Screenshot Workflow

Use this reference when turning raw simulator screenshots into commercial App Store images.

## Size Requirements

Verify current App Store Connect screenshot placeholders or official Apple documentation before final export. Do not rely on memory when submitting to the Store.

Capture dimensions and marketing output dimensions are different concerns:

- Raw screenshots should match the simulator screen.
- Marketing screenshots should match the App Store Connect slots requested for the app listing.

## Composition Guidance

Create separate specs for iPhone and iPad.

For each output:

- Use a real raw screenshot.
- Add one compact headline and one short supporting line.
- Preserve important UI areas; do not crop controls needed to understand the feature.
- Avoid fake UI, fake data, or claims not visible in the product.
- Prefer 5-7 screenshots per device unless the user asks otherwise.

## Suggested Story Arc

1. Organize everything in one place.
2. Add or edit the core object quickly.
3. Track details, status, or history.
4. Find/filter/organize content.
5. Show the distinctive differentiator.

## Output Structure

```text
AppStoreScreenshots/
  marketing/
    iphone/
      01-...
    ipad/
      01-...
    spec.json
```

## Validation

After generation:

1. Check every PNG's pixel width and height.
2. Open at least one image per device class.
3. Confirm no text overlaps, no raw screenshot is blurry, and no device frame hides relevant UI.
4. Keep raw and marketing assets separate.
