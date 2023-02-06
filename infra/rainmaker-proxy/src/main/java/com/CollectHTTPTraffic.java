package com;

import org.json.JSONArray;
import org.json.JSONObject;
import java.io.FileWriter;
import java.io.IOException;
import static com.Rainmaker.curTestStatDirWithSeq;

public class CollectHTTPTraffic {
    JSONArray traffic;
    final int trafficLength;

    /**
     * Constructor for HTTP traffic collection.
     * @param _traffic
     */
    public CollectHTTPTraffic(JSONArray _traffic) {
        trafficLength = _traffic.length();
        traffic       = _traffic;
    }

    /**
     * Truncate the body of the HTTP requests in the traffic.
     * Some requests (e.g., Azure Table service) may have very large json size,
     * (e.g., body part in entity batch operation) so truncate the body.
     */
    public void truncateRequestBody() {
        for (int i = 0; i < trafficLength; ++i) {
            JSONObject jsonObj = traffic.getJSONObject(i);
            if (jsonObj.has("httpRequest")) {
                JSONObject request = jsonObj.getJSONObject("httpRequest");
                if (request.has("body"))
                    request.remove("body");
            }
        }
    }

    /**
     * Preserve the HTTP traffic into JSON file on the disk.
     */
    public void saveHTTPTraffic() {
        try {
            FileWriter fileWriter
                    = new FileWriter(curTestStatDirWithSeq + "/request.json", true);
            fileWriter.write(traffic.toString());
            fileWriter.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}


