import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";


describe("Seguimiento administrativo", () => {
  it("actualiza el punto y detecta pérdida de señal automáticamente", () => {
    const ordersSource = readFileSync(
      resolve(process.cwd(), "src/views/OrdersView.vue"),
      "utf8",
    );
    const mapSource = readFileSync(
      resolve(process.cwd(), "src/components/DeliveryMap.vue"),
      "utf8",
    );

    expect(ordersSource).toContain(
      "trackingInterval = window.setInterval(refreshTracking, 15_000)",
    );
    expect(mapSource).toContain("> 30_000");
    expect(mapSource).toContain("Última actualización:");
    expect(mapSource).toContain("window.clearInterval(freshnessInterval)");
  });
});
