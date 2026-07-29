import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import StatusNotice from "../src/components/StatusNotice.vue";

describe("StatusNotice", () => {
  it("no ocupa espacio sin mensaje", () => {
    const wrapper = mount(StatusNotice);
    expect(wrapper.find(".notice").exists()).toBe(false);
  });

  it("expone el mensaje como estado accesible", () => {
    const wrapper = mount(StatusNotice, {
      props: { message: "Plato guardado.", kind: "success" },
    });
    expect(wrapper.text()).toContain("Plato guardado.");
    expect(wrapper.attributes("role")).toBe("status");
    expect(wrapper.classes()).toContain("notice-success");
  });
});
