def run():

    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.express as px
    import altair as alt
    from datetime import datetime

    # Cargar datos
    df_np = pd.read_csv("MPNP.csv", sep=";")

    # Limpiar datos
    df_np = df_np.rename(columns={
        "Fecha": "Fecha",
        "Draw": "Ronda",
        "Tipo": "Tipo",
        "Subtipo": "Subtipo",
        "Number of Letters of Advice to Apply issued": "Invitaciones",
        "Ranking score of lowest-ranked candidate invited": "Puntaje mínimo"
    })

    df_np["Fecha"] = pd.to_datetime(df_np["Fecha"], dayfirst=True)
    df_np = df_np.sort_values("Fecha")
    
    # Limpiar filas vacías o con datos inválidos
    df_np = df_np.dropna(subset=["Fecha"])
    df_np = df_np[df_np["Invitaciones"].notna()]

    # Sidebar
    st.sidebar.title("Filtros")
    
    # Filtro por Tipo
    st.sidebar.header("Tipo de Programa")
    tipos_unicos = df_np["Tipo"].sort_values().unique()
    selecciones_tipo = {}
    for tipo in tipos_unicos:
        selecciones_tipo[tipo] = st.sidebar.checkbox(tipo, value=False, key=f"tipo_{tipo}")
    
    tipos_seleccionados = [tipo for tipo, seleccionado in selecciones_tipo.items() if seleccionado]
    df_np_filtrado = df_np[df_np["Tipo"].isin(tipos_seleccionados)]

    # Filtro por Subtipo
    st.sidebar.header("Subtipo")
    subtipos_unicos = df_np_filtrado["Subtipo"].dropna().sort_values().unique()
    selecciones_subtipo = {}
    for subtipo in subtipos_unicos:
        selecciones_subtipo[subtipo] = st.sidebar.checkbox(subtipo, value=False, key=f"subtipo_{subtipo}")
    
    subtipos_seleccionados = [subtipo for subtipo, seleccionado in selecciones_subtipo.items() if seleccionado]
    if subtipos_seleccionados:  # Solo filtrar si hay subtipos seleccionados
        df_np_filtrado = df_np_filtrado[df_np_filtrado["Subtipo"].isin(subtipos_seleccionados) | df_np_filtrado["Subtipo"].isna()]

    # Filtro por Año
    st.sidebar.header("Año")
    años_unicos = df_np["Fecha"].dt.year.sort_values().unique()
    selecciones_año = {}
    for año in años_unicos:
        selecciones_año[año] = st.sidebar.checkbox(str(año), value=True, key=f"año_{año}")
    
    años_seleccionados = [año for año, seleccionado in selecciones_año.items() if seleccionado]
    df_np_filtrado = df_np_filtrado[df_np_filtrado["Fecha"].dt.year.isin(años_seleccionados)]

    # Contenido principal
    st.title("Manitoba Provincial Nominee Program (MPNP)")

    # Enlace oficial
    st.markdown(
        "Official MPNP website [Manitoba Provincial Nominee Program](https://immigratemanitoba.com/notices/eoi-draw/)",
        unsafe_allow_html=True
    )

    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de invitaciones", "{:,}".format(df_np_filtrado["Invitaciones"].sum()))
    
    promedio = df_np_filtrado["Puntaje mínimo"].mean()
    col2.metric(
        "Puntaje mínimo promedio",
        0 if pd.isna(promedio) else int(promedio)
    )
    if not df_np_filtrado["Fecha"].dropna().empty:
        fecha_max = df_np_filtrado["Fecha"].max()
        dias = (datetime.today().date() - fecha_max.date()).days
    else:
        fecha_max = df_np["Fecha"].max()
        dias = (datetime.today().date() - fecha_max.date()).days
    col3.metric("Días desde el último sorteo", dias)
    
    with col4:
        ref_value = st.number_input("Mi puntaje", value=None, placeholder="Ingrese un valor", format="%0f")
    
    gh1, gh2 = st.columns(2)
    
    with gh1:

            # Gráfico 1: Puntaje mínimo por fecha
            fig1 = px.line(df_np_filtrado, x="Fecha", y="Puntaje mínimo", color="Subtipo",
                        title="Puntaje mínimo por ronda", markers=True)
            
            fig1.add_vline(x="2025-01-01",line_dash="dash", line_color="gray")
            
            # Añadir línea de referencia si existe
            if ref_value is not None:
                try:
                    num_value = float(ref_value)
                    if not pd.isna(num_value):
                        fig1.add_hline(y=num_value, line_dash="dash", line_color="red", 
                                    annotation_text=f"Mi puntaje: {num_value}", 
                                    annotation_position="top left")
                except (ValueError, TypeError):
                    st.sidebar.warning("Por favor ingrese un valor numérico válido")

            # Ajustes de diseño
            fig1.update_layout(
                height=400,
                margin=dict(t=40, l=0, r=0, b=0),
                xaxis=dict(
                    tickangle=-45,
                    tickfont=dict(size=10)
                ),
                legend=dict(orientation="h", y=-0.3)  # leyenda horizontal debajo
            )
            st.plotly_chart(fig1, use_container_width=True)
        
    with gh2:

        # Gráfico 2: Invitaciones por fecha
        fig2 = px.line(df_np_filtrado, x="Fecha", y="Invitaciones", color="Subtipo",
                    title="Invitaciones emitidas a lo largo del tiempo", markers=True)
        
        fig2.add_vline(x="2025-01-01",line_dash="dash", line_color="gray")
        
        
        fig2.update_layout(
            height=400,
            margin=dict(t=40, l=0, r=0, b=0),
            xaxis=dict(
                tickangle=-45,
                tickfont=dict(size=10)
            ),
            legend=dict(orientation="h", y=-0.3)
        )
        st.plotly_chart(fig2, use_container_width=True)

    
    
    # Mostrar tabla de datos
    # with st.expander("Ver tabla de datos"):
    #     st.dataframe(df_np_filtrado)