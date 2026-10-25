using UnityEngine;

/// <summary>
/// Raises a water surface to an absolute water level (metres, NGF-IGN69).
/// Attach to the water plane. The terrain mesh must use the same vertical
/// offset that pointcloud_to_mesh.py subtracted (see *.offset.json).
/// </summary>
public class WaterLevelController : MonoBehaviour
{
    [Tooltip("Z offset (metres) subtracted from LiDAR heights when the mesh was exported.")]
    public float verticalOffset = 0f;

    [Tooltip("Seconds to reach a new level (smooth rise reads better in VR).")]
    public float transitionSeconds = 2.5f;

    [SerializeField] private float targetLevel = 0f;
    private float velocity;

    public float CurrentLevel => transform.position.y + verticalOffset;

    /// <summary>Set absolute water level in metres.</summary>
    public void SetLevel(float absoluteLevelMetres)
    {
        targetLevel = absoluteLevelMetres;
    }

    /// <summary>Hook for a UI slider (0..1) mapped onto a range.</summary>
    public float sliderMin = 0f, sliderMax = 3f;
    public void SetLevelNormalized(float t)
    {
        SetLevel(Mathf.Lerp(sliderMin, sliderMax, t));
    }

    void Update()
    {
        float y = targetLevel - verticalOffset;
        Vector3 p = transform.position;
        p.y = Mathf.SmoothDamp(p.y, y, ref velocity, transitionSeconds);
        transform.position = p;
    }
}
