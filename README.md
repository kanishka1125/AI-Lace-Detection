# AI Fabric & Lace Visual Search

An AI-powered visual and text search system for a fabric and lace
catalogue.

## 1. Project Goal

The goal is to build a Google Lens-style search experience specifically
for a fabric/lace catalogue.

``` text
                    USER
                     |
             +-------+-------+
             |               |
             v               v
        IMAGE SEARCH     TEXT SEARCH
             |               |
             v               v
       IMAGE UPLOAD      TEXT QUERY
             |               |
             v               v
       FashionSigLIP    Catalogue Metadata
             |           Search / Matching
             v               |
       Image Embedding       |
             |               |
             v               |
            FAISS <----------+
             |
             v
     Similar Catalogue Items
             |
             v
        FastAPI Backend
             |
             v
       React Frontend
             |
             v
       Search Results
```

------------------------------------------------------------------------

# 2. The Main Problem We Solved

The project initially used a vision-language model to generate catalogue
names:

``` text
IMAGE
  |
  v
Florence-2
  |
  v
Free-form description
  |
  v
Extract words
  |
  v
Product name
```

This did **not** work reliably for the catalogue.

A catalogue image can contain:

``` text
Actual lace/fabric
        +
Background
        +
Labels
        +
Paper
        +
Other surrounding material
```

The generated description sometimes focused on the label or background
rather than the actual textile.

For example:

``` text
Red/Green Sequin Fabric
        |
        v
Description mentions white label
        |
        v
Keyword extraction sees "white"
        |
        v
"White Lace"   <-- WRONG
```

This caused many incorrect names and colors.

------------------------------------------------------------------------

# 3. The New Approach

We changed the pipeline from **description-based naming** to **direct
visual classification**.

### OLD

``` text
Image
  |
  v
Florence-2 Description
  |
  v
Keyword Extraction
  |
  v
Name
```

### NEW

``` text
Image
  |
  v
Multiple Image Crops
  |
  v
FashionSigLIP
  |
  +------------+-------------+
  |            |             |
  v            v             v
COLOR       PATTERN       TEXTILE TYPE
  |            |             |
  +------------+-------------+
               |
               v
       Aggregate Predictions
               |
               v
       Controlled Product Name
```

This is the key architectural improvement.

------------------------------------------------------------------------

# 4. Why FashionSigLIP?

The project uses **Marqo FashionSigLIP** because the problem is
specifically related to fashion/textile imagery.

Instead of asking a model to write an arbitrary description, we compare
the image against controlled visual concepts.

For example:

``` text
IMAGE
  |
  v
FashionSigLIP
  |
  +--> White
  +--> Black
  +--> Pink
  +--> Red
  +--> Blue
  +--> Green
  +--> Beige
  +--> Brown
  ...
```

Similarly for patterns:

``` text
Floral
Leaf
Striped
Zigzag
Diamond
Geometric
Scallop
Sequin
Embroidered
Mesh
...
```

And textile types:

``` text
Lace
Fabric
Floral Lace
Guipure Lace
Corded Lace
Embroidered Lace
Mesh Lace
Sequin Fabric
...
```

The final name is created from these controlled attributes.

Example:

``` text
Brown + Floral + Floral Lace
              |
              v
       Brown Floral Lace
```

or:

``` text
Gold + Sequin + Sequin Fabric
              |
              v
       Gold Sequin Fabric
```

------------------------------------------------------------------------

# 5. Multi-Crop Strategy

A major issue was background/label interference.

Therefore, the metadata pipeline uses multiple views:

``` text
                  ORIGINAL IMAGE
                       |
          +------------+------------+
          |            |            |
          v            v            v
       Original    10% Crop    Central Crop
          |            |            |
          +------------+------------+
                       |
                       v
                 FashionSigLIP
                       |
                       v
              Average Predictions
```

The intention is to make the actual textile more important than borders,
labels, and surrounding objects.

------------------------------------------------------------------------

# 6. Catalogue

The catalogue currently contains:

``` text
74 Product IDs
89 Image Files
```

This distinction matters because one product can contain more than one
image.

The structure is approximately:

``` text
backend/
|
+-- catalogue/
|   |
|   +-- LACE1001/
|   |   +-- LACE1001_0.jpeg
|   |
|   +-- LACE1002/
|   |   +-- LACE1002_0.jpeg
|   |
|   +-- ...
|
+-- metadata/
    +-- catalogue_metadata.json
```

The final metadata process works at the **product level**:

``` text
Product ID
    |
    v
All images for that product
    |
    v
Image-level predictions
    |
    v
Aggregate predictions
    |
    v
One product-level metadata record
```

------------------------------------------------------------------------

# 7. Metadata Pipeline

The final metadata-generation process is:

``` text
Catalogue Product
       |
       v
Find Product Images
       |
       v
Create Multiple Crops
       |
       v
FashionSigLIP
       |
       +------------+-------------+
       |            |             |
       v            v             v
     Color       Pattern       Type
       |            |             |
       +------------+-------------+
                    |
                    v
             Aggregate Results
                    |
                    v
              Product Name
                    |
                    v
       catalogue_metadata.json
```

The system does **not** force every item to be called lace.

Possible outputs include:

``` text
White Floral Lace
Blue Zigzag Lace
Brown Floral Lace
Gold Sequin Fabric
Green Fabric
Pink Lace
```

------------------------------------------------------------------------

# 8. Image Search Architecture

Image search is the main AI retrieval pipeline:

``` text
User Uploads Image
       |
       v
React Frontend
       |
       v
FastAPI Backend
       |
       v
FashionSigLIP
       |
       v
Image Embedding
       |
       v
FAISS
       |
       v
Similarity Ranking
       |
       v
Top Catalogue Matches
       |
       v
FastAPI JSON
       |
       v
React Result Cards
```

The important distinction is:

``` text
Query Image
     |
     v
Embedding
     |
     v
Vector Similarity
     |
     v
Visually Similar Products
```

The system is therefore not relying on exact product names for image
retrieval.

------------------------------------------------------------------------

# 9. Text Search Architecture

Text search is handled separately:

``` text
User enters:
"floral lace"
       |
       v
React Frontend
       |
       v
FastAPI Backend
       |
       v
Catalogue Metadata Search
       |
       v
Relevant Products
       |
       v
React Frontend
```

Therefore:

``` text
IMAGE SEARCH
FashionSigLIP + FAISS
        |
        v
Visual Similarity


TEXT SEARCH
Catalogue Metadata
        |
        v
Text Relevance
```

Keeping the two pipelines separate makes them easier to debug and
improve.

------------------------------------------------------------------------

# 10. Frontend

The frontend is built with:

-   React
-   Vite
-   JavaScript
-   Tailwind-style utility classes
-   Lucide React icons

The frontend handles:

-   Image upload
-   Image preview
-   Text search
-   Search button
-   Loading state
-   API calls
-   Product cards
-   Similarity display
-   Catalogue metadata
-   Search history/analytics UI

The frontend communicates with FastAPI over HTTP.

------------------------------------------------------------------------

# 11. Backend

The backend uses:

-   Python
-   FastAPI
-   Uvicorn

Responsibilities include:

-   Receiving image-search requests
-   Receiving text-search requests
-   Calling the visual retrieval pipeline
-   Returning search results
-   Serving catalogue images
-   Connecting the AI/search layer to the React UI

Development server:

``` powershell
uvicorn app:app --reload
```

FastAPI documentation:

``` text
http://127.0.0.1:8000/docs
```

------------------------------------------------------------------------

# 12. Vector Search

FAISS is used for visual similarity search.

``` text
Catalogue Image 1 ---> Embedding 1
Catalogue Image 2 ---> Embedding 2
Catalogue Image 3 ---> Embedding 3
...
Catalogue Image N ---> Embedding N

                       |
                       v
                      FAISS
                       ^
                       |
                 Query Image
                       |
                       v
                    Embedding
                       |
                       v
                Similarity Search
                       |
                       v
                  Top Results
```

This means images are compared through learned visual representations
instead of simple pixel-level comparison.

------------------------------------------------------------------------

# 13. Technology Stack

## Frontend

-   React
-   Vite
-   JavaScript
-   Tailwind-style utility classes
-   Lucide React

## Backend

-   Python
-   FastAPI
-   Uvicorn

## AI / Computer Vision

-   PyTorch
-   Marqo FashionSigLIP
-   OpenCLIP
-   Hugging Face Transformers
-   Pillow

## Search

-   FAISS
-   Vector embeddings
-   Similarity ranking

## Data

-   JSON
-   Local image catalogue
-   Structured catalogue metadata

## Development

-   VS Code
-   Conda
-   PowerShell
-   Git
-   GitHub

------------------------------------------------------------------------

# 14. Project Structure

``` text
AI-Lace-Detection/
|
+-- backend/
|   |
|   +-- app.py
|   |
|   +-- catalogue/
|   |   +-- LACE1001/
|   |   +-- LACE1002/
|   |   +-- ...
|   |
|   +-- metadata/
|   |   +-- catalogue_metadata.json
|   |
|   +-- fix_catalogue_names_v2.py
|   +-- check_random_metadata.py
|   +-- test_visual_classifier.py
|   +-- finalize_catalogue_metadata.py
|
+-- frontend/
    |
    +-- frontend-app/
        |
        +-- src/
        |   +-- App.jsx
        |
        +-- package.json
        +-- ...
```

------------------------------------------------------------------------

# 15. Running the Project

## Activate environment

``` powershell
conda activate lace_project
```

## Start backend

From the backend directory:

``` powershell
cd backend
uvicorn app:app --reload
```

## Start frontend

From the frontend application directory:

``` powershell
cd frontendrontend-app
npm run dev
```

------------------------------------------------------------------------

# 16. Problems Faced and How They Were Solved

## Problem 1 --- AI Generated Incorrect Product Names

### What happened

The original model generated names that did not match the actual images.

Examples included:

``` text
White Lace
White Floral Lace
White Striped Lace
```

for images that were actually colored fabrics, sequins, or different
patterns.

### Why

The system was extracting attributes from a free-form generated
description.

### Solution

Changed:

``` text
Image
 -> Description
 -> Keyword Extraction
 -> Name
```

to:

``` text
Image
 -> FashionSigLIP
 -> Visual Attributes
 -> Controlled Name
```

------------------------------------------------------------------------

## Problem 2 --- Background/Label Confusion

### What happened

A white label or black background could influence the predicted color.

For example:

``` text
Red fabric + white label
```

could become:

``` text
White Lace
```

### Solution

Introduced multiple image crops before FashionSigLIP classification:

``` text
Original
+
Border-removed crop
+
Central crop
```

and aggregated the predictions.

------------------------------------------------------------------------

## Problem 3 --- Florence-2 Import Error

The initial script attempted to import:

``` python
Florence2ForConditionalGeneration
```

but the installed Transformers version did not expose that class.

### Solution

The loading approach was changed to a compatible Transformers approach,
but after testing the actual metadata quality, Florence-2 was no longer
used for attribute generation.

The project therefore solved both the technical loading problem and the
deeper model-selection problem.

------------------------------------------------------------------------

## Problem 4 --- FashionSigLIP Transformers Loading Error

FashionSigLIP initially produced:

``` text
NotImplementedError:
Cannot copy out of meta tensor; no data!
```

when loaded through the Transformers AutoModel route.

### Solution

FashionSigLIP was loaded through OpenCLIP:

``` python
open_clip.create_model_and_transforms(
    "hf-hub:Marqo/marqo-fashionSigLIP"
)
```

This successfully loaded the model on CPU and produced useful visual
predictions.

------------------------------------------------------------------------

## Problem 5 --- Matplotlib Missing

The catalogue inspection script initially failed with:

``` text
ModuleNotFoundError:
No module named 'matplotlib'
```

### Solution

Installed:

``` powershell
pip install matplotlib
```

This enabled random catalogue inspection and metadata validation.

------------------------------------------------------------------------

## Problem 6 --- 74 Products vs 89 Images

The catalogue had:

``` text
74 products
89 images
```

### Solution

The final metadata process works at product level and aggregates
predictions from all images belonging to the same product.

------------------------------------------------------------------------

## Problem 7 --- Backend `ModuleNotFoundError`

Running:

``` powershell
uvicorn backend.app:app --reload
```

from inside the backend folder caused:

``` text
ModuleNotFoundError: No module named 'backend'
```

### Solution

The Uvicorn module path was matched to the working directory:

``` powershell
uvicorn app:app --reload
```

when already inside `backend`.

------------------------------------------------------------------------

## Problem 8 --- Frontend `npm run dev` Error

Running `npm run dev` from the wrong directory produced:

``` text
npm error Missing script: "dev"
```

### Solution

The command was run from the actual Vite project:

``` powershell
cd frontendrontend-app
npm run dev
```

------------------------------------------------------------------------

## Problem 9 --- Failed Frontend Fetch

The frontend initially showed:

``` text
Failed to fetch
```

### Solution

The frontend API calls were corrected so that:

``` text
Image Search -> Image Search Backend API
Text Search  -> Text Search Backend API
```

rather than disabling text search.

------------------------------------------------------------------------

## Problem 10 --- Search Images Not Displaying Correctly

Some result images were not appearing because the frontend received
relative catalogue paths.

For example:

``` text
/catalogue/LACE1018/LACE1018_0.jpeg
```

was converted to a backend URL:

``` text
http://127.0.0.1:8000/catalogue/LACE1018/LACE1018_0.jpeg
```

This allowed FastAPI to serve the catalogue images to the frontend.

------------------------------------------------------------------------

## Problem 11 --- Empty Metadata Fields

Some UI fields were empty because the catalogue did not consistently
contain values for every product.

The frontend was made defensive so missing values do not break the UI:

``` text
Missing value
     |
     v
"—"
```

The unreliable colour field was also removed from the visible
specification section rather than displaying misleading information.

------------------------------------------------------------------------

## Problem 12 --- AI Metadata Was Tested Before Full Replacement

Instead of repeatedly overwriting all products, a random sample of
catalogue images was inspected.

This exposed the actual problem:

``` text
Actual image
     |
     v
Wrong generated metadata
```

The testing step prevented us from continuing with an unreliable
metadata-generation approach.

------------------------------------------------------------------------

# 17. Validation Strategy

The project now follows this validation pattern:

``` text
Change AI Pipeline
       |
       v
Test Small Sample
       |
       v
Inspect Results
       |
       +---- BAD ----> Fix Pipeline
       |
       +---- GOOD ---> Process Full Catalogue
```

This is much safer than applying an AI-generated transformation to the
complete dataset immediately.

------------------------------------------------------------------------

# 18. Current Final Architecture

``` text
                         USER
                           |
              +------------+------------+
              |                         |
              v                         v
         IMAGE SEARCH              TEXT SEARCH
              |                         |
              v                         v
        React Frontend            React Frontend
              |                         |
              v                         v
        FastAPI Backend            FastAPI Backend
              |                         |
              v                         v
       FashionSigLIP             Catalogue Metadata
              |                   Search Logic
              v                         |
       Image Embedding                  |
              |                         |
              v                         v
             FAISS              Relevant Products
              |                         |
              +------------+------------+
                           |
                           v
                    Search Results
                           |
                           v
                    React Product UI
```

Catalogue metadata is maintained separately:

``` text
Catalogue Images
       |
       v
Multiple Crops
       |
       v
FashionSigLIP
       |
       +----> Color
       |
       +----> Pattern
       |
       +----> Textile Type
       |
       v
Aggregate by Product
       |
       v
Controlled Product Name
       |
       v
catalogue_metadata.json
```

------------------------------------------------------------------------

# 19. Current Status

Completed:

-   [x] Catalogue loaded
-   [x] 74 products / 89 images identified
-   [x] FastAPI backend
-   [x] React/Vite frontend
-   [x] Image upload
-   [x] Image search
-   [x] Text search
-   [x] FashionSigLIP integration
-   [x] OpenCLIP loading
-   [x] FAISS visual retrieval
-   [x] Catalogue image serving
-   [x] Frontend result mapping
-   [x] Random metadata validation
-   [x] Visual attribute testing
-   [x] Multi-crop strategy
-   [x] Metadata backup before final update

Next:

``` text
Final Metadata
      |
      v
Search Validation
      |
      v
Image Search Accuracy
      |
      v
Text Search Validation
      |
      v
Final UI Polish
      |
      v
GitHub / Deployment
```

------------------------------------------------------------------------

# 20. Final Takeaway

The important architectural lesson from this project is:

``` text
DO NOT:
Image
  -> Free-form AI Description
  -> Extract random words
  -> Product Name
```

Instead:

``` text
DO:
Image
  -> Visual Representation
  -> Controlled Attributes
  -> Structured Metadata
  -> Product Name
```

And for retrieval:

``` text
Query Image
  -> FashionSigLIP Embedding
  -> FAISS
  -> Similar Catalogue Products
```

The result is a system where **visual retrieval and catalogue metadata
are separated**, making the project easier to evaluate, debug, improve,
and scale.
