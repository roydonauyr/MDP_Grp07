package com.example.MDPGroup7.ui.main;
import org.json.*;
public class JSONProcessing {
    public static String JSONStringProcessing (String original_msg) throws JSONException {
        JSONObject obj = new JSONObject(original_msg);
        String type = obj.getString("type");
        return obj.getString("value");
    }
}
