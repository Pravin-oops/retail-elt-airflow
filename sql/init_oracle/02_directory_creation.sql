-- Run this as RETAIL_DW
-- Create a logical reference to the physical folder inside the Docker container
-- Note: /data is the path we defined in docker-compose.yml
CREATE OR REPLACE DIRECTORY source_data_dir AS '/data';
/
