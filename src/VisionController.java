import java.util.ArrayList;

import org.opencv.core.Mat;
import org.opencv.core.MatOfPoint;

import edu.wpi.cscore.VideoSource;
import edu.wpi.first.wpilibj.vision.VisionPipeline;
import edu.wpi.first.wpilibj.vision.VisionRunner;
import edu.wpi.first.wpilibj.vision.VisionThread;

/**
 * Vision system for the 2017 Steamworks competition
 *
 * All your cameras are belong to me.
 *
 * @author Skyview StormBots - FRC #2811
 *
 */
public class VisionController {

	/*
	 * Overall components we need:
	 *  - A vision thread running the GRIP pipeline, which may also pass data back to additional processing routines
	 *      - The callback/notifier pipeline can update some stats about the last frame processed
	 *  - The ability to switch cameras, perhaps with the GRIP routines attached to them
	 *  - Output the angular deviation from the target
	 *  - Output a distance to the target (likely based on target area)
	 *  - Output selected statistics to the SmartDashboard
	 *  - Potentially output drive cameras to the SmartDashboard to help the drivers with visibility
	 *      - If net bandwidth permits!
	 */

	private CameraSpec camInfo;
	
	private VisionMode mode;
	
	private VideoSource shooterSource;

	private VideoSource gearSource;

	private VisionPipeline shooterPipeline;

	private VisionPipeline gearPipeline;
	
	private VisionRunner<BoilerLedPipeline> shooterRunner = new VisionRunner<BoilerLedPipeline>(
			this.shooterSource,
			(BoilerLedPipeline) this.shooterPipeline,
			this.shooterListener
	);
	
	private VisionRunner<PegDetectionPipeline> gearRunner = new VisionRunner<PegDetectionPipeline>(
			this.gearSource,
			(PegDetectionPipeline) this.gearPipeline,
			this.gearListener
	);

	private VisionRunner.Listener<BoilerLedPipeline> shooterListener;

	private VisionRunner.Listener<PegDetectionPipeline> gearListener;

	private VisionThread shooterThread; // needs: VideoSource, Pipeline, VisionRunner.Listener

	private VisionThread gearThread; // needs: VideoSource, Pipeline, VisionRunner.Listener
	
	Object imgLock = new Object();
	
	private Mat rgbFilteredImage;
	
	private ArrayList<MatOfPoint> filteredContours;
/*

Dummy VideoSource

source = new VideoCamera(0);

source.setResolution(1280, 720);

*/
	public VisionController(VideoSource shooterSource, VideoSource gearSource, CameraSpec camInfo,
							VisionPipeline shooterPipeline, VisionPipeline gearPipeline)
	{
		this.shooterSource = shooterSource;
		this.gearSource = gearSource;

		this.camInfo = camInfo;
		
		this.shooterPipeline = shooterPipeline;
		this.gearPipeline = gearPipeline;

		this.shooterListener = (BoilerLedPipeline p) -> {
			try {
				imgLock.wait();
			} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			this.rgbFilteredImage = p.rgbThresholdOutput();
			this.filteredContours = p.filterContoursOutput();
			imgLock.notify();
		};
		
		
		this.gearListener = (PegDetectionPipeline p) -> {
			try {
				imgLock.wait();
			} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} // TODO: Catch InterruptedEx
			this.rgbFilteredImage = p.rgbThresholdOutput();
			this.filteredContours = p.filterContoursOutput();
			imgLock.notify();
		};

		// start the pipeline threads
		// note: this automatically invokes the runForever method on the runner
		this.shooterThread = new VisionThread(this.shooterRunner);
		this.gearThread = new VisionThread(this.gearRunner);
		
		this.mode = VisionMode.BOILER_HIGH;
	}
	
	public double getXAngleToTarget() {
		
		// multiply our camera's degrees/pixel by (centerX - imageWidth/2)
		// therefore, a negative angle represents the target being to the left
		// of the camera/robot and also signals a need to turn left to
		// align with the target
		
		//TODO: Remove
		return 0;
	}
	
	public double getYAngleToTarget() {
		
		// multiply our camera's degrees/pixel by (centerY - imageHeight/2)
		// and add it to tiltAngle
		
		//TODO: Remove
		return 0;
	}
	
	public double getDistanceToTarget() {
		
		//TODO: Remove
		return 0;
	}
	
}
