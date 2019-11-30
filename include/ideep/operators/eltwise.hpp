#ifndef IDEEP_OPERATORS_ELTWISE_HPP
#define IDEEP_OPERATORS_ELTWISE_HPP

namespace ideep {

struct eltwise_forward : public dnnl::eltwise_forward {

  using super = dnnl::eltwise_forward;

  static void compute(const tensor& src,
                      tensor& dst,
                      algorithm aalgorithm = algorithm::eltwise_relu,
                      prop_kind aprop_kind = prop_kind::forward,
                      float alpha = 0.0,
                      float beta = 0.0,
                      const engine& aengine = engine::cpu_engine()) {
    auto src_in = src;
    if (aalgorithm != algorithm::eltwise_relu && src.get_data_type() != data_type::f32) {
      src_in.reinit(src.get_dims(), data_type::f32);
      IDEEP_ENFORCE(src.has_scale(), "Can not find scales");
      IDEEP_ENFORCE(src.get_scale().size() == 1, "Incorrect scale size");
      src_in.feed_from(src);
    }
    auto src_desc = src_in.get_desc();

    auto pd = primitive_desc(
        {aprop_kind, aalgorithm, src_desc, alpha, beta}, aengine);

    if (dst != src) {
      dst.reinit(src_in.get_descriptor());
      if (src_in.has_scale()) dst.set_scale(src_in.get_scale());
    }

    super(pd).execute(stream::default_stream(),
                      {{DNNL_ARG_SRC, src_in}, {DNNL_ARG_DST, dst}});

    if (dst.has_scale() && aalgorithm == algorithm::eltwise_relu && dst.get_data_type() == data_type::s8) {
      tensor::desc dst_u8_desc = dst.get_desc().to_type(data_type::u8);
      dst.set_desc(dst_u8_desc);
    }
  }
};

struct eltwise_backward : public dnnl::eltwise_backward {
  using super = dnnl::eltwise_backward;
  // If grady and x had different format, performance is bad.
  // TODO: Seeking a single shot solution.
  static void compute(const tensor& src,
                      const tensor& diff_dst,
                      tensor& diff_src,
                      algorithm aalgorithm = algorithm::eltwise_relu,
                      float alpha = 0.0,
                      float beta = 0.0,
                      const engine& aengine = engine::cpu_engine()) {
  auto src_desc = src.get_desc();
  auto diff_dst_ = diff_dst.reorder_if_differ_in(src_desc);

  auto forward_hints = eltwise_forward::primitive_desc(
      {prop_kind::forward, aalgorithm, src_desc, alpha, beta}, aengine);
  auto pd =
      primitive_desc({aalgorithm, diff_dst.get_desc(), src_desc, alpha, beta},
                     aengine, forward_hints);

  auto expected_diff_dst = diff_dst_.reorder_if_differ_in(pd.diff_dst_desc());
  auto expected_src = src.reorder_if_differ_in(pd.src_desc());
  diff_src.reinit_if_necessary(pd.diff_src_desc());

  super(pd).execute(stream::default_stream(),
                    {{DNNL_ARG_DIFF_DST, expected_diff_dst},
                    {DNNL_ARG_SRC, expected_src},
                    {DNNL_ARG_DIFF_SRC, diff_src}});
  }
};
}  // namespace ideep

#endif
