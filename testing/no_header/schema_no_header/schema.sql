-- Generated DDL for postgresql
-- Generated at: 2025-08-24T17:08:23.559586

CREATE TABLE "customers" (
    "column_1" INTEGER NOT NULL,
    "column_2" INTEGER NOT NULL,
    "column_3" VARCHAR(42) NOT NULL,
    "column_4" VARCHAR(4) NOT NULL,
    PRIMARY KEY ("column_1")
);

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

CREATE TABLE "orders" (
    "column_1" INTEGER NOT NULL,
    "column_2" INTEGER NOT NULL,
    "column_3" VARCHAR(18) NOT NULL,
    "column_4" TIMESTAMP NOT NULL,
    "column_5" TIMESTAMP NOT NULL,
    "column_6" TIMESTAMP NOT NULL,
    "column_7" TIMESTAMP NOT NULL,
    "column_8" TIMESTAMP NOT NULL,
    PRIMARY KEY ("column_1"),
    FOREIGN KEY ("column_2") REFERENCES "customers" ("column_1")
);

CREATE TABLE "sellers" (
    "column_1" INTEGER NOT NULL,
    "column_2" VARCHAR(14) NOT NULL,
    PRIMARY KEY ("column_1")
);
