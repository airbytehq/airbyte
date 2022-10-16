#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.utils.helpers import get_instance_number


def test_get_instance_number():
    class ClassA:
        pass

    class ClassB(ClassA):
        pass

    class MixIn:
        pass

    class ClassC(MixIn, ClassB):
        pass

    class_a_instance1 = ClassA()
    class_a_instance2 = ClassA()
    class_b_instance1 = ClassB()
    class_b_instance2 = ClassB()
    class_c_instance1 = ClassC()
    class_c_instance2 = ClassC()

    assert get_instance_number(class_a_instance1) == 1
    assert get_instance_number(class_a_instance2) == 2
    assert get_instance_number(class_b_instance1) == 1
    assert get_instance_number(class_b_instance2) == 2
    assert get_instance_number(class_c_instance1) == 1
    assert get_instance_number(class_c_instance2) == 2
    del class_c_instance1
    class_c_instance3 = ClassC()
    assert get_instance_number(class_c_instance3) == 3
