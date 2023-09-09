package com.example.MDPGroup7.ui.main;

import android.content.Context;

import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentManager;
import androidx.fragment.app.FragmentPagerAdapter;

public class CommsAdapter extends FragmentPagerAdapter {

    private final Context mContext;

    public CommsAdapter(Context context, FragmentManager fm) {
        super(fm);
        mContext = context;
    }

    @Override
    public Fragment getItem(int position) {
        return CommsFragment.newInstance(position +1);
    }

    @Override
    public int getCount() {
        return 1;
    }

}
