
public class CameraSpec {
	
	private double dfov;
	
	private double focalLength;
	
	private int pixelsX, pixelsY;
	
	private double height;
	
	private double tiltAngle;
	
	private double sensorDimD;
	
	private VisionMode mode;
	
	public CameraSpec(double dfov, double focalLength, int pxX, int pxY,
					  double height, double tiltAngle, double sensorDimD)
	{
		this.dfov = dfov;
		this.focalLength = focalLength;
		this.pixelsX = pxX;
		this.pixelsY = pxY;
		this.height = height;
		this.tiltAngle = tiltAngle;
		this.sensorDimD = sensorDimD;
		
	}
	
	public double getDFov(){
		return this.dfov;
	}
	
	public double getFocalLength(){
		return this.focalLength;
	}
	
	public int getPxX(){
		return this.pixelsX;
	}
	
	public int getPxY(){
		return this.pixelsY;
	}
	
	public double getHeight(){
		return this.height;
	}
	
	public double getTiltAngle(){
		return this.tiltAngle;
	}
	
	public double getSensorDim(){
		return this.sensorDimD;
	}
	
	
}
