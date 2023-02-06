package com;
import java.io.*;
import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

public class Infra {
    /**
     * This is the main entrance of Rainmaker.
     * @param args
     * @throws Exception
     */
    public static void main(String[] args) throws Exception {
        // Read Rainmaker configuration from config.json
        final File configFile = new File(System.getProperty("user.dir"), "config_generated.json");
        InputStream is        = new DataInputStream(new FileInputStream(configFile));
        JSONTokener token     = new JSONTokener(is);
        JSONArray configArray = new JSONArray(token);

        // Parse the json object corresponding to each cloud application under test
        for (int i = 0; i < configArray.length(); i++) {
            try {
                JSONObject config   = configArray.getJSONObject(i);
                boolean skipFlag    = config.getBoolean("skip");
                if (skipFlag)
                    continue;
                Rainmaker rainmaker = new Rainmaker(config);

                // Start the Rainmaker proxy at the beginning of each test round
                rainmaker.startRainmakerProxy();
                System.out.println("Start mock server successfully!");
                rainmaker.rainmakerTest();

                // Stop the Rainmaker proxy at the end of each test round
                rainmaker.stopRainmakerProxy();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
}