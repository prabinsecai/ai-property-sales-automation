# Database

SQLite stores the complete property catalog with stable `property_id`, rental, availability,
location, amenity, and audit timestamp fields. `scripts.seed` is idempotent and creates 36
fictional records.

Core columns: `property_id`, `address`, `suburb`, `city`, `state`, `weekly_rent`,
`bedrooms`, `bathrooms`, `parking`, `pet_policy`, `lease_duration`, `nearby_facilities`,
`availability_status`, `available_date`, `created_at`, and `updated_at`.
