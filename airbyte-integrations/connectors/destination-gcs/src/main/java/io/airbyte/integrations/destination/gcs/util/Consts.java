/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs.util;

public class Consts {

  public static final String EXPECTED_ROLES = "storage.multipartUploads.abort, storage.multipartUploads.create, "
      + "storage.objects.create, storage.objects.delete, storage.objects.get, storage.objects.list";

  public static final String CHECK_ACTIONS_TMP_FILE_NAME = "test";

  // Uploads this text size will automatically use a multipart upload strategy, while uploads smaller
  // than this threshold will use
  // a single connection to upload the whole object even if multipart upload option is ON.
  public final static String DUMMY_MIDDLE_SIZE_TEXT =
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque malesuada lacinia aliquet. Nam feugiat mauris vel magna dignissim feugiat. Nam non dapibus sapien, ac mattis purus. Donec mollis libero erat, a rutrum ipsum pretium id. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Integer nec aliquam leo. Aliquam eu dictum augue, a ornare elit.\n"
          + "\n"
          + "Nulla viverra blandit neque. Nam blandit varius efficitur. Nunc at sapien blandit, malesuada lectus vel, tincidunt orci. Proin blandit metus eget libero facilisis interdum. Aenean luctus scelerisque orci, at scelerisque sem vestibulum in. Nullam ornare massa sed dui efficitur, eget volutpat lectus elementum. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Integer elementum mi vitae erat eleifend iaculis. Nullam eget tincidunt est, eget tempor est. Sed risus velit, iaculis vitae est in, volutpat consectetur odio. Aenean ut fringilla elit. Suspendisse non aliquet massa. Curabitur suscipit metus nunc, nec porttitor velit venenatis vel. Fusce vestibulum eleifend diam, lobortis auctor magna.\n"
          + "\n"
          + "Etiam maximus, mi feugiat pharetra mattis, nulla neque euismod metus, in congue nunc sem nec ligula. Curabitur aliquam, risus id convallis cursus, nunc orci sollicitudin enim, quis scelerisque nibh dui in ipsum. Suspendisse mollis, metus a dapibus scelerisque, sapien nulla pretium ipsum, non finibus sem orci et lectus. Aliquam dictum magna nisi, a consectetur urna euismod nec. In pulvinar facilisis nulla, id mollis libero pulvinar vel. Nam a commodo leo, eu commodo dolor. In hac habitasse platea dictumst. Curabitur auctor purus quis tortor laoreet efficitur. Quisque tincidunt, risus vel rutrum fermentum, libero urna dignissim augue, eget pulvinar nibh ligula ut tortor. Vivamus convallis non risus sed consectetur. Etiam accumsan enim ac nisl suscipit, vel congue lorem volutpat. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce non orci quis lacus rhoncus vestibulum nec ut magna. In varius lectus nec quam posuere finibus. Vivamus quis lectus vitae tortor sollicitudin fermentum.\n"
          + "\n"
          + "Pellentesque elementum vehicula egestas. Sed volutpat velit arcu, at imperdiet sapien consectetur facilisis. Suspendisse porttitor tincidunt interdum. Morbi gravida faucibus tortor, ut rutrum magna tincidunt a. Morbi eu nisi eget dui finibus hendrerit sit amet in augue. Aenean imperdiet lacus enim, a volutpat nulla placerat at. Suspendisse nibh ipsum, venenatis vel maximus ut, fringilla nec felis. Sed risus mi, egestas quis quam ullamcorper, pharetra vestibulum diam.\n"
          + "\n"
          + "Praesent finibus scelerisque elit, accumsan condimentum risus mattis vitae. Donec tristique hendrerit facilisis. Curabitur metus purus, venenatis non elementum id, finibus eu augue. Quisque posuere rhoncus ligula, et vehicula erat pulvinar at. Pellentesque vel quam vel lectus tincidunt congue quis id sapien. Ut efficitur mauris vitae pretium iaculis. Aliquam consectetur iaculis nisi vitae laoreet. Integer vel odio quis diam mattis tempor eget nec est. Donec iaculis facilisis neque, at dictum magna vestibulum ut. Sed malesuada non nunc ac consequat. Maecenas tempus lectus a nisl congue, ac venenatis diam viverra. Nam ac justo id nulla iaculis lobortis in eu ligula. Vivamus et ligula id sapien efficitur aliquet. Curabitur est justo, tempus vitae mollis quis, tincidunt vitae felis. Vestibulum molestie laoreet justo, nec mollis purus vulputate at.";

}
