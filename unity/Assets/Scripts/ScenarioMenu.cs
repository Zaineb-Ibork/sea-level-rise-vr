using System.Collections.Generic;
using System.IO;
using TMPro;
using UnityEngine;
using UnityEngine.Networking;

/// <summary>
/// Loads StreamingAssets/scenarios.json (same file as the Python pipeline)
/// and fills a TMP_Dropdown. Selecting a scenario moves the water.
/// Works in a world-space Canvas with XR Interaction Toolkit UI.
/// </summary>
public class ScenarioMenu : MonoBehaviour
{
    [System.Serializable] public class Scenario { public string name; public int year; public float rise_m; }
    [System.Serializable] public class Config { public float baseline_water_level_m; public List<Scenario> scenarios; }

    public WaterLevelController water;
    public TMP_Dropdown dropdown;
    public TMP_Text caption;
    public string fileName = "scenarios.json";

    private Config cfg;

    System.Collections.IEnumerator Start()
    {
        string path = Path.Combine(Application.streamingAssetsPath, fileName);
        string json;
        // On Android (Quest) StreamingAssets lives inside the APK: must use UnityWebRequest.
        using (var req = UnityWebRequest.Get(path))
        {
            yield return req.SendWebRequest();
            if (req.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError($"Cannot read {path}: {req.error}");
                yield break;
            }
            json = req.downloadHandler.text;
        }
        cfg = JsonUtility.FromJson<Config>(json);

        dropdown.ClearOptions();
        var labels = new List<string>();
        foreach (var s in cfg.scenarios) labels.Add($"{s.name} - {s.year}");
        dropdown.AddOptions(labels);
        dropdown.onValueChanged.AddListener(Select);
        Select(0);
    }

    public void Select(int i)
    {
        var s = cfg.scenarios[i];
        float level = cfg.baseline_water_level_m + s.rise_m;
        water.SetLevel(level);
        if (caption) caption.text = $"{s.name}, {s.year}\nSea level +{s.rise_m:0.00} m";
    }
}
