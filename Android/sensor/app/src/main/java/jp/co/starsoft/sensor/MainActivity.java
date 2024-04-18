package jp.co.starsoft.sensor;

import android.app.Activity;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.hardware.Sensor;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;

import com.google.android.material.floatingactionbutton.FloatingActionButton;
import com.google.android.material.snackbar.Snackbar;

import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;

import android.os.Handler;
import android.os.Message;
import android.view.Display;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.View;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.ProtocolException;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;


import org.json.JSONArray;
import org.json.JSONObject;

public class MainActivity extends Activity {

    private Button btnGet;
    private Button btnDraw;
    private SensorView sensorView = null;
    private LinearLayout linearLayout = null;
    private LinearLayout linearTopLayout = null;
    private LinearLayout mLlayoutBottomButtons = null;
    private ImageView imageView = null;
    private List<CheckBox> checkBoxes = new ArrayList<>();
    private List<TextView> dataTextViews = new ArrayList<>();
    private List<TextView> timeTextViews = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Display display = getWindowManager().getDefaultDisplay();
        setContentView(R.layout.activity_main);
        sensorView = (SensorView)findViewById(R.id.sensorview);
        sensorView.setActivity(this);
        linearLayout = findViewById(R.id.linearLayout);
        linearTopLayout = findViewById(R.id.linearTopLayout);
        mLlayoutBottomButtons = findViewById(R.id.mLlayoutBottomButtons);
        imageView = (ImageView)findViewById(R.id.imageView);

        findViews();

    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    private void findViews() {
        btnGet = findViewById(R.id.btnGet);
        btnGet.setOnClickListener(getData);
        btnDraw = findViewById(R.id.btnDraw);
        btnDraw.setOnClickListener(drawData);
        linearLayout.setVisibility(View.VISIBLE);
        linearTopLayout.setVisibility(View.VISIBLE);
        mLlayoutBottomButtons.setVisibility(View.VISIBLE);
        sensorView.setVisibility(View.GONE);
        imageView.setVisibility(View.GONE);
    }

    @RequiresApi(api = Build.VERSION_CODES.JELLY_BEAN_MR1)
    private void setLineLayout(StringBuilder sensorData) {
        List<String> dataList = new ArrayList<>();
        List<String> timeList = new ArrayList<>();
        String dictionaryString = sensorData.toString();
        try {
            // Parse JSON array
            JSONArray jsonArray = null;
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.KITKAT) {
                jsonArray = new JSONArray(dictionaryString);
            }

            // Process each object in the JSON array
            for (int i = 0; i < jsonArray.length(); i++) {
                // Get JSON object at index i
                JSONObject jsonObject = jsonArray.getJSONObject(i);
                // Extract data and timestamp from JSON object
                String data = jsonObject.getString("data");
                String timestamp = jsonObject.getString("timestamp");
                dataList.add(data);
                timeList.add(timestamp);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                LinearLayout layout = findViewById(R.id.linearLayout);
                int numTextFields = dataList.size();
                int margin = 10;
                for (int i = 0; i < numTextFields; i++) {
                    LinearLayout newRow = new LinearLayout(MainActivity.this);
                    LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                            LinearLayout.LayoutParams.WRAP_CONTENT,
                            LinearLayout.LayoutParams.WRAP_CONTENT
                    );
                    newRow.setLayoutParams(params);
                    newRow.setOrientation(LinearLayout.HORIZONTAL);
                    params.setMargins(margin, margin, margin, margin);
                    CheckBox checkBox = new CheckBox(MainActivity.this);
                    checkBox.setTag(String.valueOf(i));
                    checkBox.setLayoutParams(params);
                    checkBoxes.add(checkBox);
                    newRow.addView(checkBox);
                    TextView textView = new TextView(MainActivity.this);
                    textView.setTag("textviewTime" + String.valueOf(i));
                    textView.setLayoutParams(params);
                    textView.setText(timeList.get(i));
                    timeTextViews.add(textView);
                    newRow.addView(textView);
                    textView = new TextView(MainActivity.this);
                    textView.setTag("textviewData" + String.valueOf(i));
                    textView.setLayoutParams(params);
                    textView.setText(dataList.get(i));
                    dataTextViews.add(textView);
                    newRow.addView(textView);
                    layout.addView(newRow);
                }
            }
        });

    }

    private View.OnClickListener getData = new View.OnClickListener() {
        public void onClick(View v) {
            // Execute the AsyncTask to perform the GET request
            new GetDataTask().execute("http://133.18.23.48:5000/sensor");
        }
    };

    private class GetDataTask extends AsyncTask<String, Void, String> {

        @RequiresApi(api = Build.VERSION_CODES.JELLY_BEAN_MR1)
        @Override
        protected String doInBackground(String... strings) {
            String urlString = strings[0];
            try {
                // Create URL object
                URL url = new URL(urlString);

                // Create connection
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setRequestMethod("GET");

                // Read the response
                InputStream inputStream = connection.getInputStream();
                BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));
                StringBuilder response = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    response.append(line);
                }
                setLineLayout(response);
                // Close resources
                reader.close();
                inputStream.close();
                connection.disconnect();

                // Return the response
                return response.toString();
            } catch (IOException e) {
                e.printStackTrace();
                return null;
            }
        }

        @Override
        protected void onPostExecute(String result) {
            if (result != null) {
            } else {
            }
        }
    }

    private View.OnClickListener drawData = new View.OnClickListener() {
        List<String> dataList = new ArrayList<>();
        List<String> timeList = new ArrayList<>();
        public void onClick(View v) {
            for (CheckBox checkBox : checkBoxes) {
                if (checkBox.isChecked()) {
                    String tag = (String)checkBox.getTag();
                    int index = Integer.parseInt(tag);
                    String data = dataTextViews.get(index).getText().toString();
                    dataList.add(data);
                    String timeData = timeTextViews.get(index).getText().toString();
                    timeList.add(timeData);
                }
            }
            if (dataList.size() > 0) {
                linearLayout.setVisibility(View.GONE);
                linearTopLayout.setVisibility(View.GONE);
                mLlayoutBottomButtons.setVisibility(View.GONE);
                sensorView.setVisibility(View.VISIBLE);
            }
//            sensorView.setData(dataList, timeList);
            new GetImageTask().execute("http://133.18.23.48:5000/image/" + timeList.get(0) + "/" + timeList.get(1));
            timeList.clear();
            dataList.clear();
        }
    };


    private class GetImageTask extends AsyncTask<String, Void, Bitmap> {

        @RequiresApi(api = Build.VERSION_CODES.JELLY_BEAN_MR1)
        @Override
        protected Bitmap doInBackground(String... strings) {
            String urlString = strings[0];
            Bitmap bitmap = null;
            try {
                // Create URL object
                URL url = new URL(urlString);

                // Create connection
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setDoInput(true);
                connection.connect();
                InputStream input = connection.getInputStream();
                bitmap = BitmapFactory.decodeStream(input);
                connection.disconnect();
                showGraph(bitmap);
                // Return the response
                return bitmap;
            } catch (IOException e) {
                e.printStackTrace();
                return null;
            }
        }

    }

    private void showGraph(Bitmap bitmap) {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                try {
                    linearLayout.setVisibility(View.GONE);
                    linearTopLayout.setVisibility(View.GONE);
                    mLlayoutBottomButtons.setVisibility(View.GONE);
                    sensorView.setVisibility(View.GONE);
                    imageView.setVisibility(View.VISIBLE);
                    // Get a reference to the ImageView in your layout
                    ImageView imageView = findViewById(R.id.imageView);

                    // Set the bitmap to the ImageView
                    imageView.setImageBitmap(bitmap);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
    }

    @Override
    public void onBackPressed() {
        linearLayout.setVisibility(View.VISIBLE);
        linearTopLayout.setVisibility(View.VISIBLE);
        mLlayoutBottomButtons.setVisibility(View.VISIBLE);
        sensorView.setVisibility(View.GONE);
        imageView.setVisibility(View.GONE);
    }
}
