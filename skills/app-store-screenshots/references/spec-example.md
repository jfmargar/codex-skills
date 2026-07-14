# Example Spec

Use the bundled generator with a JSON file shaped like this:

```json
{
  "brand": "Librarian",
  "source_root": "/absolute/path/to/raw-screenshots",
  "output_root": "/absolute/path/to/final-marketing-shots",
  "shots": [
    {
      "device": "iphone",
      "source": "01-library-home.png",
      "output": "01-library-home.png",
      "size": [1284, 2778],
      "title": "Tu biblioteca, de un vistazo",
      "subtitle": "Libros, colecciones y autores en una portada clara y elegante."
    },
    {
      "device": "ipad",
      "source": "ipad-01-library-home.png",
      "output": "ipad-01-library-home.png",
      "size": [2064, 2752],
      "title": "Toda tu colección, en gran formato",
      "subtitle": "Una vista panorámica para explorar libros, estanterías y colecciones."
    }
  ]
}
```

Rules:

- Use absolute paths for `source_root` and `output_root`.
- Keep `iphone` and `ipad` outputs in separate subfolders.
- Set `size` to the exact placeholder or Apple-documented dimensions for the current App Store Connect slot.
- Reuse the same copy tone across the whole set.
