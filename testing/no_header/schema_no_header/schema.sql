-- Generated DDL for postgresql
-- Generated at: 2025-09-06T18:10:50.391164

CREATE TABLE "customers" (
    "column_1" INTEGER NOT NULL,
    "column_2" INTEGER NOT NULL,
    "column_3" VARCHAR(255) NOT NULL,
    "column_4" VARCHAR(255) NOT NULL,
    PRIMARY KEY ("column_1")
);

-- NORMALIZATION SUGGESTIONS:
-- [3NF] customers: Transitive dependency detected: column_4 depends on column_3, creating transitive dependency through primary key. Consider extracting to a separate 'column_3_details' columns_and_types with columns: column_3, column_4.
--   Confidence: 1.0

-- [3NF] customers: Transitive dependency detected: column_3, column_4 depends on column_2, creating transitive dependency through primary key. Consider extracting to a separate 'column_2_details' columns_and_types with columns: column_2, column_3, column_4.
--   Confidence: 1.0

CREATE TABLE "products" (
    "column_1" INTEGER NOT NULL,
    "column_2" INTEGER NOT NULL,
    "column_3" INTEGER NOT NULL,
    "column_4" INTEGER NOT NULL,
    "column_5" BOOLEAN NOT NULL,
    "column_6" INTEGER NOT NULL,
    "column_7" INTEGER NOT NULL,
    "column_8" INTEGER NOT NULL,
    "column_9" INTEGER NOT NULL,
    PRIMARY KEY ("column_1"),
    FOREIGN KEY ("column_2") REFERENCES "sellers" ("column_1"),
    FOREIGN KEY ("column_5") REFERENCES "customers" ("column_1")
);

-- NORMALIZATION SUGGESTIONS:
-- [3NF] products: Transitive dependency detected: column_6, column_7, column_8, column_4, column_5, column_3, column_2 depends on column_9, creating transitive dependency through primary key. Consider extracting to a separate 'column_9_details' columns_and_types with columns: column_9, column_6, column_7, column_8, column_4, column_5, column_3, column_2.
--   Confidence: 1.0

-- [3NF] products: Transitive dependency detected: column_9, column_7, column_8, column_4, column_5, column_3, column_2 depends on column_6, creating transitive dependency through primary key. Consider extracting to a separate 'column_6_details' columns_and_types with columns: column_6, column_9, column_7, column_8, column_4, column_5, column_3, column_2.
--   Confidence: 1.0

-- [3NF] products: Transitive dependency detected: column_9, column_6, column_8, column_4, column_5, column_3, column_2 depends on column_7, creating transitive dependency through primary key. Consider extracting to a separate 'column_7_details' columns_and_types with columns: column_7, column_9, column_6, column_8, column_4, column_5, column_3, column_2.
--   Confidence: 1.0

-- [3NF] products: Transitive dependency detected: column_9, column_6, column_7, column_4, column_5, column_3, column_2 depends on column_8, creating transitive dependency through primary key. Consider extracting to a separate 'column_8_details' columns_and_types with columns: column_8, column_9, column_6, column_7, column_4, column_5, column_3, column_2.
--   Confidence: 1.0

-- [3NF] products: Transitive dependency detected: column_9, column_6, column_7, column_8, column_5, column_3, column_2 depends on column_4, creating transitive dependency through primary key. Consider extracting to a separate 'column_4_details' columns_and_types with columns: column_4, column_9, column_6, column_7, column_8, column_5, column_3, column_2.
--   Confidence: 1.0

-- [3NF] products: Transitive dependency detected: column_9, column_6, column_7, column_8, column_4, column_5, column_2 depends on column_3, creating transitive dependency through primary key. Consider extracting to a separate 'column_3_details' columns_and_types with columns: column_3, column_9, column_6, column_7, column_8, column_4, column_5, column_2.
--   Confidence: 1.0

-- [3NF] products: Transitive dependency detected: column_9, column_6, column_7, column_8, column_4, column_5, column_3 depends on column_2, creating transitive dependency through primary key. Consider extracting to a separate 'column_2_details' columns_and_types with columns: column_2, column_9, column_6, column_7, column_8, column_4, column_5, column_3.
--   Confidence: 1.0

CREATE TABLE "orders" (
    "column_1" INTEGER NOT NULL,
    "column_2" INTEGER NOT NULL,
    "column_3" VARCHAR(255) NOT NULL,
    "column_4" TIMESTAMP NOT NULL,
    "column_5" TIMESTAMP NOT NULL,
    "column_6" TIMESTAMP NOT NULL,
    "column_7" TIMESTAMP NOT NULL,
    "column_8" TIMESTAMP NOT NULL,
    PRIMARY KEY ("column_1"),
    FOREIGN KEY ("column_2") REFERENCES "customers" ("column_1")
);

-- NORMALIZATION SUGGESTIONS:
-- [3NF] orders: Transitive dependency detected: column_7, column_8, column_4, column_5, column_3, column_2 depends on column_6, creating transitive dependency through primary key. Consider extracting to a separate 'column_6_details' columns_and_types with columns: column_6, column_7, column_8, column_4, column_5, column_3, column_2.
--   Confidence: 1.0

-- [3NF] orders: Transitive dependency detected: column_6, column_8, column_4, column_5, column_3, column_2 depends on column_7, creating transitive dependency through primary key. Consider extracting to a separate 'column_7_details' columns_and_types with columns: column_7, column_6, column_8, column_4, column_5, column_3, column_2.
--   Confidence: 1.0

-- [3NF] orders: Transitive dependency detected: column_6, column_7, column_4, column_5, column_3, column_2 depends on column_8, creating transitive dependency through primary key. Consider extracting to a separate 'column_8_details' columns_and_types with columns: column_8, column_6, column_7, column_4, column_5, column_3, column_2.
--   Confidence: 1.0

-- [3NF] orders: Transitive dependency detected: column_6, column_7, column_8, column_5, column_3, column_2 depends on column_4, creating transitive dependency through primary key. Consider extracting to a separate 'column_4_details' columns_and_types with columns: column_4, column_6, column_7, column_8, column_5, column_3, column_2.
--   Confidence: 1.0

-- [3NF] orders: Transitive dependency detected: column_6, column_7, column_8, column_4, column_3, column_2 depends on column_5, creating transitive dependency through primary key. Consider extracting to a separate 'column_5_details' columns_and_types with columns: column_5, column_6, column_7, column_8, column_4, column_3, column_2.
--   Confidence: 1.0

-- [3NF] orders: Transitive dependency detected: column_6, column_7, column_8, column_4, column_5, column_3 depends on column_2, creating transitive dependency through primary key. Consider extracting to a separate 'column_2_details' columns_and_types with columns: column_2, column_6, column_7, column_8, column_4, column_5, column_3.
--   Confidence: 1.0

CREATE TABLE "sellers" (
    "column_1" INTEGER NOT NULL,
    "column_2" VARCHAR(255) NOT NULL,
    PRIMARY KEY ("column_1")
);
