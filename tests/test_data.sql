-- We specify our primary key here to be as repeatable as possible
-- INSERT INTO example_table(id, foo) VALUES
--   (1, 'hello, world!');

-- Restart our primary key sequences here so inserting id=DEFAULT won't collide
ALTER SEQUENCE example_table_id_seq RESTART 1000;