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

	private VisionRunner.Listener<BoilerLedPipeline> shooterListener;

	private VisionRunner.Listener<PegDetectionPipeline> gearListener;

	private VisionThread shooterThread; // needs: VideoSource, Pipeline, VisionRunner.Listener

	private VisionThread gearThread; // needs: VideoSource, Pipeline, VisionRunner.Listener
/*

Dummy VideoSource

source = new VideoCamera(0);

source.setResolution(1280, 720);




*/
	public VisionController(VideoSource shooterSource, VideoSource gearSource,
							VisionPipeline shooterPipeline, VisionPipeline gearPipeline) {
		this.shooterSource = shooterSource;
		this.gearSource = gearSource;

		this.shooterPipeline = shooterPipeline;
		this.gearPipeline = gearPipeline;

		/*
		 * TODO: Add the copyPipelineOutputs methods to copy the data. Make sure to use/copy with a mutex to avoid
		 *		 crazy things happening. 
		 */
		this.shooterListener = new VisionRunner.Listener<BoilerLedPipeline>(this.shooterPipeline);
		this.gearListener = new VisionRunner.Listener<PegDetectionPipeline>(this.gearPipeline);

		this.shooterThread = new VisionThread(
							new VisionRunner<BoilerLedPipeline>(
								this.shooterSource,
								this.shooterPipeline,
								this.shooterListener
							)
		);

		this.gearThread = new VisionThread(
							new VisionRunner<PegDetectionPipeline>(
								this.gearSource,
								this.gearPipeline,
								this.gearListener
							)
		);

		this.shooterThread.runForever();
		this.gearThread.runForever();
	}

}
