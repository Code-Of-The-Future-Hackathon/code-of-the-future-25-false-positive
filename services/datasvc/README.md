# Data Model

## Node (Base table for network nodes)

- id (uuid PRIMARY KEY)
- display_name (varchar)
- latitude (decimal)
- longitude (decimal)
- node_type (enum: 'dam', 'place', 'junction')
- created_at (timestamp)
- updated_at (timestamp)

## Dam (Extends Node)

- id (uuid PRIMARY KEY, FOREIGN KEY REFERENCES Node(id))
- border_geometry (geometry(MULTIPOLYGON, 4326))
- max_volume (decimal) -- m³, maximum capacity
- description (text, default: '')

## Place (Extends Node)

- id (uuid PRIMARY KEY, FOREIGN KEY REFERENCES Node(id))
- population (integer)
- consumption_per_capita (decimal) -- m³/person/day
- water_price (decimal) -- BGN/m³
- non_dam_incoming_flow (decimal) -- m³/s
- radius (decimal) -- meters

## WaterConnection

- id (uuid PRIMARY KEY)
- source_node_id (uuid FOREIGN KEY REFERENCES Node(id))
- target_node_id (uuid FOREIGN KEY REFERENCES Node(id))
- max_flow_rate (decimal) -- m³/s, maximum flow capacity
- length (decimal) -- meters
- created_at (timestamp)
- updated_at (timestamp)

## DamBulletinMeasurement

- id (uuid PRIMARY KEY)
- dam_id (uuid FOREIGN KEY REFERENCES Dam(id))
- timestamp (timestamp)
- volume (decimal) -- m³, current volume
- fill_volume (decimal) -- m³, usable volume
- avg_incoming_flow (decimal) -- m³/s, average daily inflow
- avg_outgoing_flow (decimal) -- m³/s, average daily outflow

## SatelliteImage

- id (uuid PRIMARY KEY)
- dam_id (uuid FOREIGN KEY REFERENCES Dam(id))
- timestamp (timestamp)
- image_url (varchar)
- bounding_box (geometry(POLYGON, 4326))
- created_at (timestamp)

## UserBillForm

- id (uuid PRIMARY KEY)
- place_id (uuid FOREIGN KEY REFERENCES Place(id))
- start_date (date)
- end_date (date)
- created_at (timestamp)

## NewsletterSubscription

- id (uuid PRIMARY KEY)
- email (varchar UNIQUE)
- created_at (timestamp)
- updated_at (timestamp)

## DamAlert

- id (uuid PRIMARY KEY)
- dam_id (uuid FOREIGN KEY REFERENCES Dam(id))
- severity (enum: 'info', 'warning', 'critical')
- timestamp (timestamp)
- message (text)
- created_at (timestamp)
