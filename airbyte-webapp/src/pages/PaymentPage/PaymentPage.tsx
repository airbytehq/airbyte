import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";
import { Navigate, Route, Routes } from "react-router-dom";
import styled from "styled-components";

import HeadTitle from "components/HeadTitle";
import LoadingPage from "components/LoadingPage";
import MainPageWithScroll from "components/MainPageWithScroll";

import useRouter from "hooks/useRouter";

import PaymentNav from "./components/PaymentNav";
import { NavMenuItem } from "./components/PaymentNav";
import BillingAndPaymentPage from "./pages/BillingAndPaymentPage";
import SelectPlanPage from "./pages/SelectPlanPage";

const Content = styled.div`
  display: flex;
  flex-direction: column;
`;

const MainView = styled.div`
  width: 100%;
`;

export interface PageConfig {
  menuConfig: NavMenuItem[];
}

interface SettingsPageProps {
  pageConfig?: PageConfig;
}

export const PaymentRoute = {
  SelectPlan: "select-plan",
  BillingPayment: "billing-payment",
} as const;

const PaymentPage: React.FC<SettingsPageProps> = () => {
  const { push, pathname } = useRouter();

  const menuItems: NavMenuItem[] = [
    {
      routes: [
        {
          path: `${PaymentRoute.SelectPlan}`,
          name: <FormattedMessage id="plan.select.plan" />,
          component: SelectPlanPage,
        },
        {
          path: `${PaymentRoute.BillingPayment}`,
          name: <FormattedMessage id="plan.billing.payment" />,
          component: BillingAndPaymentPage,
        },
      ],
    },
  ];

  const onSelectMenuItem = (newPath: string) => push(newPath);
  const firstRoute = menuItems[0].routes?.[0]?.path;

  return (
    <>
      <PaymentNav data={menuItems} onSelect={onSelectMenuItem} activeItem={pathname} />
      <MainPageWithScroll headTitle={<HeadTitle titles={[{ id: "payment.tabTitle" }]} />}>
        <Content>
          <MainView>
            <Suspense fallback={<LoadingPage />}>
              <Routes>
                {menuItems
                  .flatMap((menuItem) => menuItem.routes)
                  .map(({ path, component: Component }) => (
                    <Route key={path} path={path} element={<Component />} />
                  ))}
                <Route path="*" element={<Navigate to={firstRoute} replace />} />
              </Routes>
            </Suspense>
          </MainView>
        </Content>
      </MainPageWithScroll>
    </>
  );
};

export default PaymentPage;
