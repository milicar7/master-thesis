-- Generated DDL for postgresql
-- Generated at: 2025-08-24T17:07:43.294564

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
    "product_name" VARCHAR(196) NOT NULL,
    "aisle_id" INTEGER NOT NULL,
    "department_id" INTEGER NOT NULL,
    PRIMARY KEY ("product_id"),
    FOREIGN KEY ("aisle_id") REFERENCES "aisles" ("aisle_id"),
    FOREIGN KEY ("department_id") REFERENCES "departments" ("department_id")
);

CREATE TABLE "orders" (
    "order_id" INTEGER NOT NULL,
    "user_id" INTEGER NOT NULL,
    "eval_set" VARCHAR(10) NOT NULL,
    "order_number" INTEGER NOT NULL,
    "order_dow" INTEGER NOT NULL,
    "order_hour_of_day" INTEGER NOT NULL,
    "days_since_prior_order" DECIMAL(10,1),
    PRIMARY KEY ("order_id")
);

CREATE TABLE "departments" (
    "department_id" INTEGER NOT NULL,
    "department" VARCHAR(30) NOT NULL,
    PRIMARY KEY ("department_id")
);

CREATE TABLE "aisles" (
    "aisle_id" INTEGER NOT NULL,
    "aisle" VARCHAR(58) NOT NULL,
    PRIMARY KEY ("aisle_id")
);
