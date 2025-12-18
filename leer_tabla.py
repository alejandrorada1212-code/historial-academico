components.html(
    f"""
    <div style="
        padding:20px;
        margin-bottom:20px;
        border-radius:16px;
        background:linear-gradient(145deg,#0b1220,#020617);
        color:white;
        max-width:420px;
        font-family:Roboto, sans-serif;
    ">
        <h3 style="margin-bottom:6px;">{materia}</h3>
        <p style="opacity:0.75; margin-bottom:14px;">
            <b>Código:</b> {codigo_mat} | <b>Créditos:</b> {creditos}
        </p>

        <!-- CORTES -->
        <div style="margin-bottom:16px;">

            {f'''
            <div style="display:flex; justify-content:space-between;
                        padding:12px 14px; margin-bottom:8px;
                        border-radius:10px; background:#020617;">
                <div>
                    <div style="font-size:14px;">Primer corte</div>
                    <div style="font-size:12px; color:#38bdf8;">30%</div>
                </div>
                <div style="font-size:22px; font-weight:bold;">{p1}</div>
            </div>
            ''' if p1 not in (None, 0) else ""}

            {f'''
            <div style="display:flex; justify-content:space-between;
                        padding:12px 14px; margin-bottom:8px;
                        border-radius:10px; background:#020617;">
                <div>
                    <div style="font-size:14px;">Segundo corte</div>
                    <div style="font-size:12px; color:#38bdf8;">30%</div>
                </div>
                <div style="font-size:22px; font-weight:bold;">{p2}</div>
            </div>
            ''' if p2 not in (None, 0) else ""}

            {f'''
            <div style="display:flex; justify-content:space-between;
                        padding:12px 14px;
                        border-radius:10px; background:#020617;">
                <div>
                    <div style="font-size:14px;">Examen final</div>
                    <div style="font-size:12px; color:#38bdf8;">40%</div>
                </div>
                <div style="font-size:22px; font-weight:bold;">{p3}</div>
            </div>
            ''' if p3 not in (None, 0) else ""}

        </div>

        <!-- NOTA FINAL -->
        {f'''
        <div style="
            background:{color};
            padding:14px;
            border-radius:12px;
            font-size:26px;
            font-weight:bold;
            width:190px;
            text-align:center;
            color:black;
        ">
            Final: {final}
        </div>
        ''' if final is not None else '''
        <div style="opacity:0.6; font-style:italic;">
            Sin notas registradas
        </div>
        '''}

    </div>
    """,
    height=480
)
