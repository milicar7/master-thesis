-- Generated DDL for postgresql
-- Generated at: 2025-09-21T15:26:11.480342

CREATE TABLE "order_products" (
    "order_id" INTEGER NOT NULL,
    "product_id" INTEGER NOT NULL,
    "add_to_cart_order" INTEGER NOT NULL,
    "reordered" BOOLEAN NOT NULL,
    PRIMARY KEY ("order_id", "product_id"),
    FOREIGN KEY ("product_id") REFERENCES "products" ("product_id")
);

CREATE TABLE "products" (
    "product_id" INTEGER NOT NULL,
    "product_name" VARCHAR(255) NOT NULL,
    "aisle_id" INTEGER NOT NULL,
    "department_id" INTEGER NOT NULL,
    PRIMARY KEY ("product_id"),
    FOREIGN KEY ("aisle_id") REFERENCES "aisles" ("aisle_id"),
    FOREIGN KEY ("department_id") REFERENCES "departments" ("department_id")
);

-- NORMALIZATION SUGGESTIONS:
-- [3NF] products: Transitive dependency detected: department_id, aisle_id depends on product_name, creating transitive dependency through primary key. Consider extracting to a separate 'product_name_details' columns_and_types with columns: product_name, department_id, aisle_id.
--   Confidence: 1.0

-- [3NF] products: Transitive dependency detected: department_id depends on aisle_id, creating transitive dependency through primary key. Consider extracting to a separate 'aisle_id_details' columns_and_types with columns: aisle_id, department_id.
--   Confidence: 0.9

CREATE TABLE "orders" (
    "order_id" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL,
    "eval_set" VARCHAR(255) NOT NULL,
    "order_number" INTEGER NOT NULL,
    "order_dow" INTEGER NOT NULL,
    "order_hour_of_day" INTEGER NOT NULL,
    "days_since_prior_order" DECIMAL(18,6),
    PRIMARY KEY ("order_id")
);

CREATE TABLE "departments" (
    "department_id" INTEGER NOT NULL,
    "department" VARCHAR(255) NOT NULL,
    PRIMARY KEY ("department_id")
);

CREATE TABLE "aisles" (
    "aisle_id" INTEGER NOT NULL,
    "aisle" VARCHAR(255) NOT NULL,
    PRIMARY KEY ("aisle_id")
);
