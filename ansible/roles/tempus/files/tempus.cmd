--data /usr/local/share/tempus/data
-p 9000
-c /usr/local/lib/tempus
-l dynamic_multi_plugin
-l sample_road_plugin
-L /home/osm/{{osm_pbf_file}}
-d "dbname={{osm_database}} user={{osm_username}} port={{pg_port}}"
