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

	private VideoSource shooterSource;

	private VideoSource gearSource;

	private VisionPipeline shooterPipeline;

	private VisionPipeline gearPipeline;
	
	private VisionRunner<BoilerLedPipeline> shooterRunner = new VisionRunner<BoilerLedPipeline>(
			this.shooterSource,
			(BoilerLedPipeline) this.shooterPipeline,
			this.shooterListener
	);
	
	private VisionRunner gearRunner = new VisionRunner<PegDetectionPipeline>(
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
	public VisionController(VideoSource shooterSource, VideoSource gearSource,
							VisionPipeline shooterPipeline, VisionPipeline gearPipeline)
	{
		this.shooterSource = shooterSource;
		this.gearSource = gearSource;

		this.shooterPipeline = shooterPipeline;
		this.gearPipeline = gearPipeline;

		this.shooterListener = (BoilerLedPipeline p) -> {
			imgLock.wait();
			this.rgbFilteredImage = p.rgbThresholdOutput();
			this.filteredContours = p.filterContoursOutput();
			imgLock.notify();
		};
		
		
		this.gearListener = (PegDetectionPipeline p) -> {
			imgLock.wait(); // TODO: Catch InterruptedEx
			this.rgbFilteredImage = p.rgbThresholdOutput();
			this.filteredContours = p.filterContoursOutput();
			imgLock.notify();
		};

		this.shooterThread = new VisionThread(this.shooterRunner);

		this.gearThread = new VisionThread(this.gearRunner);

		// if you run this, it'll block forever. need to figure out how to make that
		// not happen
		this.shooterRunner.runForever();
		this.gearRunner.runForever();
	}
	
	
}
