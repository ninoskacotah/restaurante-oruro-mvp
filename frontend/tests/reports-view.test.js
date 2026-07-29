import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ReportsView from "../src/views/ReportsView.vue";
import { apiRequest } from "../src/services/api.js";

vi.mock("../src/services/api.js", () => ({
  apiRequest: vi.fn(),
}));

describe("ReportsView", () => {
  beforeEach(() => {
    apiRequest.mockReset();
  });

  it("presenta las cifras recibidas del backend", async () => {
    apiRequest.mockResolvedValue({
      fecha: "2026-07-29",
      ventas_dia: "250.50",
      pedidos_contabilizados: 4,
      platos_mas_pedidos: [
        { plato_id: 1, nombre: "Plato registrado", cantidad: 6 },
      ],
      tiempo_promedio_entrega_minutos: "32.25",
    });

    const wrapper = mount(ReportsView);
    await flushPromises();

    expect(wrapper.text()).toContain("Bs 250.50");
    expect(wrapper.text()).toContain("4 pedidos contabilizados");
    expect(wrapper.text()).toContain("Plato registrado");
    expect(wrapper.text()).toContain("32.25 min");
  });

  it("explica cuando no existen entregas completas", async () => {
    apiRequest.mockResolvedValue({
      fecha: "2026-07-29",
      ventas_dia: "0.00",
      pedidos_contabilizados: 0,
      platos_mas_pedidos: [],
      tiempo_promedio_entrega_minutos: null,
    });

    const wrapper = mount(ReportsView);
    await flushPromises();

    expect(wrapper.text()).toContain("Sin datos");
    expect(wrapper.text()).toContain("No existen ventas contabilizadas");
  });
});
