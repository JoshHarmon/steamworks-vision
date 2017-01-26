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
	
	private VideoSource mainShooterSource;
	
	private VideoSource gearSource;
	
	private VisionPipeline shooterPipeline;
	
	private VisionPipeline gearPipeline;
	
	private VisionRunner.Listener mainShooterListener;
	
	private VisionRunner.Listener gearListener;
	
	private VisionThread mainShooterThread; // needs: VideoSource, Pipeline, VisionRunner.Listener
	
	private VisionThread gearThread; // needs: VideoSource, Pipeline, VisionRunner.Listener
	
	public VisionController(VideoSource shooterSource, VideoSource gearSource,
							VisionPipeline shooterPipeline, VisionPipeline gearPipeline) {
		this.mainShooterSource = shooterSource;
		this.gearSource = gearSource;
		
		this.shooterPipeline = shooterPipeline;
		this.gearPipeline = gearPipeline;
		
		
	}
	
}
