package com.example.MDPGroup7.ui.main;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.Dictionary;
import java.util.Hashtable;

public class JSONProcessing {
    public static String JSONStringProcessing (String original_msg) throws JSONException {
        JSONObject obj = new JSONObject(original_msg);
        String type = obj.getString("type");
        if (type.equals("imageRec")) {
            Dictionary<String, String> image_dict= new Hashtable<>();
            image_dict.put("1", "11");
            image_dict.put("2", "12");
            image_dict.put("3", "13");
            image_dict.put("4", "14");
            image_dict.put("5", "15");
            image_dict.put("6", "16");
            image_dict.put("7", "17");
            image_dict.put("8", "18");
            image_dict.put("9", "19");
            image_dict.put("A", "20");
            image_dict.put("B", "21");
            image_dict.put("C", "22");
            image_dict.put("D", "23");
            image_dict.put("E", "24");
            image_dict.put("F", "25");
            image_dict.put("G", "26");
            image_dict.put("H", "27");
            image_dict.put("S", "28");
            image_dict.put("T", "29");
            image_dict.put("U", "30");
            image_dict.put("V", "31");
            image_dict.put("W", "32");
            image_dict.put("X", "33");
            image_dict.put("Y", "34");
            image_dict.put("Z", "35");
            image_dict.put("UP", "36");
            image_dict.put("DOWN", "37");
            image_dict.put("RIGHT", "38");
            image_dict.put("LEFT", "39");
            image_dict.put("STOP", "40");

            JSONObject obj1 = new JSONObject(obj.getString("value"));
            String image_key = obj1.getString("image_id");
            String obstacle_id = obj1.getString("obstacle_id");
            if(image_key.equals("0")){
                return "Image Not Recognized";
            }
            else{
                String image_id = image_dict.get(image_key);
                String s = "TARGET," + obstacle_id + ",";
                if(image_id == null)
                    s += image_key;
                else
                    s += image_id;
                return s;
            }

        }

        if(type.equals("location")){
            JSONObject obj1 = new JSONObject(obj.getString("value"));
            String d = obj1.getString("d");
            String s1 = "";
            switch (d){
                case "0":
                    s1 = "N";
                    break;
                case "2":
                    s1 = "E";
                    break;
                case "4":
                    s1 = "S";
                    break;
                case "6":
                    s1 = "W";
                    break;
            }
            String s = "ROBOT," + obj1.getString("x") + "," + obj1.getString("y") + "," + s1;
            return s;
        }
        return obj.getString("value");
    }

}