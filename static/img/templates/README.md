# Template Image Placeholders

This directory should contain the following image files for the resume templates:

1. `modern.jpg` - Modern template preview image
2. `elegant.jpg` - Elegant template preview image
3. `creative.jpg` - Creative template preview image

## Creating the Images

Until proper design images are created, you can use placeholder images from services like:

- [Placeholder.com](https://placeholder.com/)
- [Placehold.co](https://placehold.co/)
- [PlaceIMG](https://placeimg.com/)

Example URLs:
```
https://placehold.co/600x400/3498db/ffffff?text=Modern+Template
https://placehold.co/600x400/8e7057/ffffff?text=Elegant+Template
https://placehold.co/600x400/6a11cb/ffffff?text=Creative+Template
```

Alternatively, you can take screenshots of the actual resume templates when they're rendered.

## Temporary Solution

To quickly fix the 404 errors, update the RESUME_TEMPLATES dictionary in app.py to use external image URLs instead of local files:

```python
RESUME_TEMPLATES = {
    'modern': {
        'name': 'Modern',
        'description': 'Clean and professional design with a blue accent color',
        'preview_img': 'https://images.unsplash.com/photo-1586281380117-5a60ae2050cc?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=80',
        'colors': ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6', '#f39c12']
    },
    # ... other templates
}
``` 