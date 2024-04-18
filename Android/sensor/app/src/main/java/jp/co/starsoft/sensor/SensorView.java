package jp.co.starsoft.sensor;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.os.Build;
import android.util.AttributeSet;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.View;
import android.widget.CheckBox;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.RequiresApi;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

public class SensorView  extends SurfaceView {
    MainActivity mainActivity;
    private SurfaceHolder surfaceHolder;
    private Paint paint;
    private List<String> dataList;
    private List<String> timeList;
    public SensorView(Context context) {
        super(context);
        init();
    }
    public SensorView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init();
    }
    @Override
    public void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        if (dataList != null) {
            // Determine the width and height of the view
            int viewWidth = getWidth();
            int viewHeight = getHeight();
            List<Integer> dataIntList = new ArrayList<>();
            List<Integer> yList = new ArrayList<>();
            String[] parts = dataList.get(0).split(",\\s*");
            int num = 0;
            for (String str : parts) {
                dataIntList.add(Integer.parseInt(str.trim()));
                yList.add(num++);
            }
            // Determine the number of data points and the interval between points
            int numPoints = Math.min(dataIntList.size(), yList.size());
            int intervalX = viewWidth / (numPoints - 1);

            // Set up the starting point for the first line
            int startX = 0;
            int startY1 =dataIntList.get(0);
            int startY2 = yList.get(0);

            // Draw lines connecting each data point
            for (int i = 1; i < numPoints; i++) {
                // Calculate the x-coordinate for the next point
                int nextX = i * intervalX;

                // Calculate the y-coordinates for the next points
                int nextY1 = dataIntList.get(i);
                int nextY2 = yList.get(i);

                try {
                    // Draw lines from the previous point to the next point for both data sets
                    canvas.drawLine(startX, startY1, nextX, nextY1, paint);
                    canvas.drawLine(startX, startY2, nextX, nextY2, paint);
                }
                catch (Exception e) {
                    e.printStackTrace();
                }

                // Update the starting point for the next line segment
                startX = nextX;
                startY1 = nextY1;
                startY2 = nextY2;
            }
        }
    }

    private void init() {
        surfaceHolder = getHolder();
        paint = new Paint();
        paint.setColor(Color.RED);
        paint.setStyle(Paint.Style.FILL);
    }

    public void setActivity(MainActivity mainActivity) {
        this.mainActivity = mainActivity;
    }



    public void setData(List<String> dataList, List<String> timeList) {
        this.dataList = dataList;
        this.timeList = timeList;
        invalidate();
    }

}
