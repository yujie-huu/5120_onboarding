import streamlit as st, pandas as pd, pydeck as pdk


def generate_map(status_df: pd.DataFrame, zone_location_map: dict | None = None):
    """
    Render the parking area map：
      zone_location_map: { zone_number: (lat, lon, status) }
      status_df: used to supplement information such as kerbside_id (must include the 'zone_number' column)
    """
    if not zone_location_map:
        st.info("No zone locations to display on the map.")
        return

    # 1) dict -> DataFrame
    rows = []
    for zone, triple in zone_location_map.items():
        if not triple or len(triple) < 2:
            continue
        lat, lon = triple[0], triple[1]
        status = triple[2] if len(triple) >= 3 else "Unknown"
        rows.append({"zone_number": str(zone), "lat": float(lat), "lon": float(lon), "status": status})
    df = pd.DataFrame(rows).dropna(subset=["lat", "lon"])
    if df.empty:
        st.info("No valid coordinates to display on the map.")
        return

    # 2) Merge additional information (such as) kerbside_id）
    if status_df is not None and not status_df.empty and "zone_number" in status_df.columns:
        # Select fields (only include those that exist)
        extra_cols = [c for c in ["kerbside_id", "status"] if c in status_df.columns]
        if extra_cols:
            df = df.merge(status_df[["zone_number", *extra_cols]].drop_duplicates("zone_number"),
                          on="zone_number", how="left", suffixes=("", "_df"))

            # If there are two statuses after the merge, the one from the dictionary shall take precedence.
            # If it is missing, the one from df shall be used.
            if "status_df" in df.columns:
                df["status"] = df["status"].fillna(df["status_df"])
                df = df.drop(columns=[c for c in ["status_df"] if c in df.columns])

    # 3) Color mapping: Unoccupied (green), Present (red), Others (gray)
    color_map = {"Unoccupied": [34, 197, 94], "Present": [239, 68, 68]}
    df["color"] = df["status"].map(lambda s: color_map.get(s, [107, 114, 128]))

    # 4) view
    view_state = pdk.ViewState(
        latitude=float(df["lat"].mean()),
        longitude=float(df["lon"].mean()),
        zoom=14,
        pitch=0
    )

    # 5) dots layer
    points = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[lon, lat]",
        get_fill_color="color",
        get_radius=12,
        radius_min_pixels=4,
        radius_max_pixels=18,
        pickable=True
    )

    # 6) Tooltip：show Zone、Status、KerbsideID
    #  Note：The tooltip mandatory field must exist in the data.
    tooltip_fields = ["Zone {zone_number}", "Status: {status}"]
    if "kerbside_id" in df.columns:
        tooltip_fields.append("KerbsideID: {kerbside_id}")
    tooltip_fields.append("[{lat}, {lon}]")
    tooltip = {"text": "\n".join(tooltip_fields)}

    deck = pdk.Deck(layers=[points], initial_view_state=view_state, tooltip=tooltip, map_style=None)
    st.pydeck_chart(deck, use_container_width=True)

    # 7) Legend
    st.markdown("""
    <div style="margin-top:8px;">
      <b>Legend:</b>
      <span style="display:inline-block;width:10px;height:10px;background:#22c55e;border-radius:50%;margin:0 6px 0 12px;"></span>Unoccupied
      <span style="display:inline-block;width:10px;height:10px;background:#ef4444;border-radius:50%;margin:0 6px 0 12px;"></span>Present
      <span style="display:inline-block;width:10px;height:10px;background:#6b7280;border-radius:50%;margin:0 6px 0 12px;"></span>Other
    </div>
    """, unsafe_allow_html=True)

