# The Data Service

A CRUD service for the dam network database.

## Setup

1. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example` and set your PostgreSQL database URL:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

## Adding new dependencies

This project uses `pip-tools` to manage dependencies. Install it in the `venv` with:

```bash
pip install pip-tools
```

Add the name of the package to the `requirements.in` file. (`requirements-dev.in` for development dependencies)

Then run `pip-compile` to update the `requirements.txt` file.

```bash
pip-compile requirements.in  # or requirements-dev.in
```

Next, you can run `pip-sync` to install the new dependencies.

```bash
pip-sync
# or
pip-sync requirements-dev.in
```

## Running the Application

Start the application with:

```bash
fastapi dev main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Running lints and formatting

Make sure you have installed the dev dependencies (see [Setup](#setup)).

To lint using `flake8`:

```bash
flake8
```

To format and sort the imports:

```bash
black .
isort .
```

## Data Model

## Diagram

![Diagram](./diagram.png)

### Node (Base table for network nodes)

- id (uuid PRIMARY KEY)
- display_name (varchar)
- latitude (decimal)
- longitude (decimal)
- node_type (enum: 'dam', 'place', 'junction')
- created_at (timestamp)
- updated_at (timestamp)

### Dam (Extends Node)

- id (uuid PRIMARY KEY, FOREIGN KEY REFERENCES Node(id))
- border_geometry (geometry(MULTIPOLYGON, 4326))
- max_volume (decimal) -- m³, maximum capacity
- description (text, default: '')

### Place (Extends Node)

- id (uuid PRIMARY KEY, FOREIGN KEY REFERENCES Node(id))
- population (integer)
- consumption_per_capita (decimal) -- m³/person/day
- water_price (decimal) -- BGN/m³
- non_dam_incoming_flow (decimal) -- m³/s
- radius (decimal) -- meters

### WaterConnection

- id (uuid PRIMARY KEY)
- source_node_id (uuid FOREIGN KEY REFERENCES Node(id))
- target_node_id (uuid FOREIGN KEY REFERENCES Node(id))
- max_flow_rate (decimal) -- m³/s, maximum flow capacity
- current_flow_rate (decimal, nullable) -- m³/s, current flow rate
- length (decimal) -- meters
- created_at (timestamp)
- updated_at (timestamp)

### DamBulletinMeasurement

- id (uuid PRIMARY KEY)
- dam_id (uuid FOREIGN KEY REFERENCES Dam(id))
- timestamp (timestamp)
- volume (decimal) -- m³, current volume
- fill_volume (decimal) -- m³, usable volume
- avg_incoming_flow (decimal) -- m³/s, average daily inflow
- avg_outgoing_flow (decimal) -- m³/s, average daily outflow

### SatelliteImage

- id (uuid PRIMARY KEY)
- dam_id (uuid FOREIGN KEY REFERENCES Dam(id))
- timestamp (timestamp)
- image_url (varchar)
- bounding_box (geometry(POLYGON, 4326))
- created_at (timestamp)

### UserBillForm

- id (uuid PRIMARY KEY)
- place_id (uuid FOREIGN KEY REFERENCES Place(id))
- start_date (date)
- end_date (date)
- created_at (timestamp)

### NewsletterSubscription

- id (uuid PRIMARY KEY)
- email (varchar UNIQUE)
- created_at (timestamp)
- updated_at (timestamp)

### DamAlert

- id (uuid PRIMARY KEY)
- dam_id (uuid FOREIGN KEY REFERENCES Dam(id))
- severity (enum: 'info', 'warning', 'critical')
- timestamp (timestamp)
- message (text)
- created_at (timestamp)
