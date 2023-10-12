namespace LAB6.Models;

public class ElectroScooter
{
    public int Id { get; set; } = default!;
    public required string Name { get; set; }
    public required double BatteryLevel { get; set; }
}