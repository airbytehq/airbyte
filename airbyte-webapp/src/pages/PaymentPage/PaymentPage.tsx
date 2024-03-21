import { CircularProgress } from "@mui/material";
import React, { useCallback, useEffect, useRef, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { BigButton, ButtonRows } from "components/base/Button/BigButton";
import HeadTitle from "components/HeadTitle";
import MainPageWithScroll from "components/MainPageWithScroll";

import { useUser } from "core/AuthContext";
import { getPaymentStatus, PAYMENT_STATUS } from "core/Constants/statuses";
import { CreateSunscriptionUrl, GetUpgradeSubscriptionDetail, UpgradeSubscription } from "core/domain/payment";
import { ProductOptionItem } from "core/domain/product";
import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";
// import { SettingsRoute } from "pages/SettingsPage/SettingsPage";
import { useAuthenticationService } from "services/auth/AuthSpecificationService";
import {
  useAsyncAction,
  useCloudPackages,
  useCloudRegions,
  useUserPlanDetail,
} from "services/payments/PaymentsService";
import { useProductOptions, usePackagesMap } from "services/products/ProductsService";

import PaymentNav from "./components/PaymentNav";
import styles from "./PaymentPage.module.scss";
import BillingPaymentStep from "./steps/BillingPaymentStep";
import SelectPlanStep from "./steps/SelectPlanStep";

const Content = styled.div`
  display: flex;
  flex-direction: column;
`;

const MainView = styled.div`
  width: 100%;
`;

export const PaymentSteps = {
  SELECT_PLAN: "SELECT_PLAN",
  BILLING_PAYMENT: "BILLING_PAYMENT",
} as const;

const PaymentPage: React.FC = () => {
  const { push } = useRouter();
  const { updateUserStatus, user } = useUser();
  const userPlanDetail = useUserPlanDetail();
  const { selectedProduct } = userPlanDetail;
  const userInfoJson = localStorage.getItem("daspire-user");
  const userInfo = JSON.parse(userInfoJson as string);
  const packages = useCloudPackages();
  const regions = useCloudRegions();
  const [currentStep, setCurrentStep] = useState<string>(PaymentSteps.SELECT_PLAN);
  const [product, setProduct] = useState<ProductOptionItem | undefined>();
  const [price, setPrice] = useState(selectedProduct?.price ?? "");
  const [cloudPackageId, setCloudPackageId] = useState(selectedProduct?.id ?? "");
  const [paymentLoading, setPaymentLoading] = useState<boolean>(false);
  const [User, setUser] = useState(null);
  const [planDetail, setPlanDetail] = useState<GetUpgradeSubscriptionDetail>();
  const [updatePlanLoading, setUpdatePlanLoading] = useState<boolean>(false);
  const [deploymentMode, setDeploymentMode] = useState("");
  const [cloudProvider, setCloudProvider] = useState(selectedProduct?.cloudProviderName ?? "");
  const [regionSelected, setRegionSelected] = useState(selectedProduct?.regionItemId !== null ? true : false);
  const [jobs, setJobs] = useState(selectedProduct?.noOfJobs ?? null);
  const [cloudItemId, setCloudItemId] = useState(selectedProduct?.cloudItemId ?? "");
  const [selectedRegion, setSelectedRegion] = useState(selectedProduct?.regionItemId ?? "");

  const [selectedInstance, setSelectedInstance] = useState(selectedProduct?.instanceItemId ?? "");

  const [instance, setInstance] = useState<any>(null);
  const [instanceSelected, setInstanceSelected] = useState(selectedProduct?.instanceItemId !== null ? true : false);
  const cloudRef = useRef(null);
  const regionScrollRef = useRef(null);
  const instanceRef = useRef(null);

  const [isCloud, setIsCloud] = useState(selectedProduct?.cloudItemId !== null ? true : false);
  const [mode, setMode] = useState(false);
  const authService = useAuthenticationService();
  const { onCreateSubscriptionURL, onGetUpgradeSubscription, onUpgradeSubscription, onInstanceSelect } =
    useAsyncAction();

  const packagesMap = usePackagesMap();

  const productOptions = useProductOptions();
  const getUserInfo = useCallback(() => {
    if (userInfo?.token) {
      authService
        .getUserInfo(userInfo?.token)
        .then((res: any) => {
          setUser?.({ ...res.data });
        })
        .catch((err) => {
          if (err.message) {
            console.log(err?.message);
          }
        });
    }
  }, [authService, setUser, userInfo.token]);

  useEffect(() => {
    if (userInfo?.token) {
      getUserInfo();
    }
  }, []);
  useEffect(() => {
    if (!selectedProduct && product === undefined) {
      setProduct(productOptions[1]);
    }
  }, [selectedProduct, productOptions, product]);

  useEffect(() => {
    if (selectedProduct && product === undefined) {
      let index = -1;
      index = productOptions.findIndex((option) => option.id === selectedProduct.id);
      if (index >= 0) {
        setProduct(productOptions[index]);
      }
    }
  }, [productOptions, selectedProduct, product]);

  useEffect(() => {
    if (selectedProduct?.cloudProviderName === "AWS" && regions?.length > 0) {
      onInstanceSelect(regions[0]?.cloudItemId)
        .then((response) => {
          setInstance(response?.data);
          // setInstanceLoading(false);
        })
        .catch((err) => {
          console.log(err);
        });
    }
  }, []);

  const handleInstanceSelect = (cloudItemId: string) => {
    onInstanceSelect(cloudItemId)
      .then((response) => {
        setInstance(response?.data);
        // setInstanceLoading(false);
      })
      .catch((err) => {
        console.log(err);
      });
  };

  const onSelectPlan = useCallback(async () => {
    setPaymentLoading(true);
    if (
      getPaymentStatus(user.status) === PAYMENT_STATUS.Subscription ||
      getPaymentStatus(user.status) === PAYMENT_STATUS.Pause_Subscription
    ) {
      onGetUpgradeSubscription({ cloudPackageId })
        .then((res: UpgradeSubscription) => {
          const detail = res?.data;
          setPlanDetail(detail);
          setPaymentLoading(false);
          setCurrentStep(PaymentSteps.BILLING_PAYMENT);
        })
        .catch(() => {
          setPaymentLoading(false);
        });
    } else {
      onCreateSubscriptionURL({ cloudPackageId })
        .then((res: CreateSunscriptionUrl) => {
          setPaymentLoading(false);
          window.open(res.data, "_self");
        })
        .catch(() => {
          setPaymentLoading(false);
        });
    }
  }, [product, selectedProduct, cloudPackageId]);

  const onUpgradePlan = useCallback(async () => {
    setUpdatePlanLoading(true);
    onUpgradeSubscription()
      .then(() => {
        updateUserStatus?.(2);
        authService
          .get()
          .then(() => {
            setUpdatePlanLoading(false);
            window.open(process.env.REACT_APP_CREATE_SPACE, "_self");
          })
          .catch(() => {
            setUpdatePlanLoading(false);
          });
      })
      .catch(() => {
        setUpdatePlanLoading(false);
      });
  }, []);

  const onBack = () => {
    if (currentStep === PaymentSteps.SELECT_PLAN) {
      push(`/${RoutePaths.Settings}/${RoutePaths.PlanAndBilling}`);
    } else {
      setCurrentStep(PaymentSteps.SELECT_PLAN);
    }
  };
  useEffect(() => {
    if (isCloud && cloudRef.current) {
      (cloudRef.current as HTMLDivElement).scrollIntoView({ behavior: "smooth" });
    }
  }, [isCloud]);
  useEffect(() => {
    if (regionSelected && regionScrollRef.current) {
      (regionScrollRef.current as HTMLDivElement).scrollIntoView({ behavior: "smooth" });
    }
  }, [regionSelected]);
  useEffect(() => {
    if (instanceSelected && instanceRef.current) {
      (instanceRef.current as HTMLDivElement).scrollIntoView({ behavior: "smooth" });
    }
  }, [instanceSelected]);
  useEffect(() => {
    if (userPlanDetail?.name === "Professional") {
      window.scrollBy(0, -500);
    }
  }, []);
  return (
    <MainPageWithScroll headTitle={<HeadTitle titles={[{ id: "payment.tabTitle" }]} />}>
      <PaymentNav steps={Object.values(PaymentSteps)} currentStep={currentStep} />
      <Content className={styles.pageContainer}>
        <MainView>
          {currentStep === PaymentSteps.SELECT_PLAN && (
            <SelectPlanStep
              product={product}
              setProduct={setProduct}
              selectedProduct={selectedProduct}
              paymentLoading={paymentLoading}
              productOptions={productOptions}
              packagesMap={packagesMap}
              onSelectPlan={onSelectPlan}
              deploymentMode={deploymentMode}
              setDeploymentMode={setDeploymentMode}
              mode={mode}
              setMode={setMode}
              regions={regions}
              cloudProvider={cloudProvider}
              setCloudProvider={setCloudProvider}
              handleInstanceSelect={handleInstanceSelect}
              setCloudItemId={setCloudItemId}
              cloudItemId={cloudItemId}
              setSelectedRegion={setSelectedRegion}
              setSelectedInstance={setSelectedInstance}
              selectedRegion={selectedRegion}
              selectedInstance={selectedInstance}
              instance={instance}
              packages={packages}
              setCloudPackageId={setCloudPackageId}
              setPrice={setPrice}
              price={price}
              jobs={jobs}
              setJobs={setJobs}
              planDetail={userPlanDetail?.planDetail}
              setInstanceSelected={setInstanceSelected}
              instanceSelected={instanceSelected}
              setIsCloud={setIsCloud}
              cloudRef={cloudRef}
              setRegionSelected={setRegionSelected}
              regionScrollRef={regionScrollRef}
              instanceRef={instanceRef}
              isCloud={isCloud}
              regionSelected={regionSelected}
              user={User}
            />
          )}
          {currentStep === PaymentSteps.BILLING_PAYMENT && (
            <BillingPaymentStep
              productPrice={Number(product?.price)}
              selectedProductPrice={selectedProduct?.price as number}
              planDetail={planDetail}
            />
          )}
        </MainView>
        <ButtonRows top="40" background="transparent">
          <BigButton secondary white onClick={onBack}>
            <FormattedMessage id="form.button.back" />
          </BigButton>
          {currentStep === PaymentSteps.BILLING_PAYMENT && (
            <BigButton isLoading={updatePlanLoading} onClick={onUpgradePlan}>
              {updatePlanLoading ? (
                <CircularProgress color="inherit" size={20} />
              ) : (
                <FormattedMessage id="plan.update.btn" />
              )}
            </BigButton>
          )}
        </ButtonRows>
      </Content>
    </MainPageWithScroll>
  );
};

export default PaymentPage;
